"""
File: backend/modules/news/engine.py
Purpose: NewsIntelligenceEngine — fetches, scores, deduplicates, and stores news.
         Production implementation. Per SPEC Section 9.2.

Called by:
  - POST /news/fetch   (on-demand via API)
  - News scheduler job (every 30 min, Phase 17)
  - Agent 7 (reads from DB after engine has run)

Flow:
  1. Fetch headlines via NewsAPICollector (+ YahooCollector fallback)
  2. Deduplicate by URL against news_articles table
  3. Score each new article with SentimentAnalyzer
  4. Persist NewsArticle + NewsSentiment rows inside a transaction
  5. Return per-symbol sentiment summaries
"""
import logging
from datetime import datetime
from sqlalchemy.orm import Session

from modules.news.sentiment import SentimentAnalyzer
from modules.news.service import NewsService

logger = logging.getLogger("app")

# Symbols we always fetch news for (watchlist)
DEFAULT_WATCHLIST = [
    "SPY", "QQQ", "AAPL", "TSLA", "NVDA", "MSFT", "AMZN",
    "GOOGL", "META", "NFLX", "GLD", "TLT",
]


class NewsIntelligenceEngine:
    def __init__(self, db: Session, cache=None):
        self.db = db
        self.cache = cache
        self._analyzer = SentimentAnalyzer()
        self._svc = NewsService(db) if db else None

    # ── Public API ────────────────────────────────────────────────────────────

    def run(self, symbols: list[str] = None) -> dict:
        """
        Fetch + score + store news for all given symbols.

        Returns:
            Dict {symbol: {"composite_score": float, "article_count": int, ...}}
        """
        symbols = symbols or DEFAULT_WATCHLIST
        results = {}

        for symbol in symbols:
            try:
                articles = self._fetch_articles(symbol)
                if not articles:
                    results[symbol] = {"composite_score": 0.0, "article_count": 0}
                    continue

                stored_count = self._store_articles(articles, symbol)
                summary = self._svc.get_sentiment_summary(symbol, hours=24) if self._svc else {}
                results[symbol] = {
                    "composite_score": summary.get("composite_score", 0.0),
                    "article_count": summary.get("article_count", stored_count),
                    "bullish_count": summary.get("bullish_count", 0),
                    "bearish_count": summary.get("bearish_count", 0),
                }
                logger.info(f"NewsEngine: {symbol} — {stored_count} new articles stored")

            except Exception as e:
                logger.error(f"NewsEngine.run failed for {symbol}: {e}")
                results[symbol] = {"composite_score": 0.0, "article_count": 0, "error": str(e)}

        if self.db:
            try:
                self.db.commit()
            except Exception as e:
                logger.error(f"NewsEngine commit failed: {e}")
                self.db.rollback()

        return results

    def get_symbol_sentiment(self, symbol: str, hours: int = 24) -> dict:
        """
        Aggregate news sentiment for a symbol over the last N hours.
        If DB is empty for symbol, fetches live and stores first.
        Used by Agent 7 (News Analyst) as complement to collector fallback.
        """
        if self._svc:
            summary = self._svc.get_sentiment_summary(symbol, hours=hours)
            if summary["article_count"] > 0:
                return summary

        # No stored data — fetch live
        articles = self._fetch_articles(symbol)
        if not articles:
            return {
                "symbol": symbol, "period_hours": hours,
                "composite_score": 0.0, "bullish_count": 0,
                "bearish_count": 0, "neutral_count": 0,
                "article_count": 0, "top_headlines": [],
            }

        # Score in-memory without storing (DB may be None)
        scored = self._score_articles(articles)
        composites = [s["composite_score"] for s in scored]
        composite_avg = sum(composites) / len(composites) if composites else 0.0
        bull = sum(1 for s in composites if s > 0.05)
        bear = sum(1 for s in composites if s < -0.05)
        neu  = len(composites) - bull - bear

        headlines = [a.get("title") or a.get("headline", "") for a in articles[:5]]

        return {
            "symbol": symbol, "period_hours": hours,
            "composite_score": round(composite_avg, 4),
            "bullish_count": bull, "bearish_count": bear, "neutral_count": neu,
            "article_count": len(articles), "top_headlines": headlines,
        }

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _fetch_articles(self, symbol: str) -> list[dict]:
        """
        Fetch news from all available sources.
        Returns normalized list of article dicts.
        """
        articles = []

        # Source 1: Yahoo Finance (no key required)
        try:
            from modules.market_data.collectors.yahoo_collector import YahooFinanceCollector
            yc = YahooFinanceCollector()
            yahoo_arts = yc.fetch_news(symbol, limit=20)
            for a in yahoo_arts:
                articles.append({
                    "title": a.get("title", ""),
                    "source": a.get("source", "Yahoo Finance"),
                    "url": a.get("url") or a.get("link", ""),
                    "published_at": a.get("published_at"),
                    "content": a.get("summary", ""),
                    "symbols": [symbol],
                })
        except Exception as e:
            logger.debug(f"Yahoo news fetch failed for {symbol}: {e}")

        # Source 2: NewsAPI (requires key)
        try:
            from modules.market_data.collectors.newsapi_collector import NewsAPICollector
            nc = NewsAPICollector()
            news_arts = nc.fetch_news(symbol, limit=20)
            for a in news_arts:
                articles.append({
                    "title": a.get("title", ""),
                    "source": a.get("source", "NewsAPI"),
                    "url": a.get("url", ""),
                    "published_at": a.get("published_at"),
                    "content": a.get("content", ""),
                    "symbols": [symbol],
                })
        except Exception as e:
            logger.debug(f"NewsAPI fetch failed for {symbol}: {e}")

        # Deduplicate by URL
        seen_urls = set()
        unique = []
        for a in articles:
            url = a.get("url", "")
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique.append(a)
        return unique

    def _score_articles(self, articles: list[dict]) -> list[dict]:
        """Score articles without DB storage. Returns sentiment dicts."""
        results = []
        for art in articles:
            headline = art.get("title") or art.get("headline", "")
            body = art.get("content") or art.get("description") or art.get("summary", "")
            results.append(self._analyzer.analyze(headline, body))
        return results

    def _store_articles(self, articles: list[dict], symbol: str) -> int:
        """
        Score and persist articles + sentiments.
        Returns count of newly stored articles (skips duplicates).
        """
        if not self._svc:
            return 0

        stored = 0
        for art in articles:
            url = art.get("url", "")
            if not url:
                continue  # skip articles without URL (can't deduplicate)

            headline = art.get("title") or art.get("headline", "")
            if not headline:
                continue

            # Parse published_at
            pub_at = art.get("published_at")
            if isinstance(pub_at, str):
                try:
                    pub_at = datetime.fromisoformat(pub_at.replace("Z", "+00:00"))
                except ValueError:
                    pub_at = datetime.utcnow()
            elif pub_at is None:
                pub_at = datetime.utcnow()

            # Sentiment scoring
            body = art.get("content") or art.get("description") or art.get("summary", "")
            sent_result = self._analyzer.analyze(headline, body)

            article_row = self._svc.store_article(
                headline=headline,
                source=art.get("source", "Unknown"),
                url=url,
                published_at=pub_at,
                symbols=art.get("symbols", [symbol]),
                sentiment_score=sent_result["composite_score"],
                impact_score=abs(sent_result["composite_score"]),
            )

            if article_row and article_row.id:
                self._svc.store_sentiment(
                    article_id=article_row.id,
                    symbol=symbol,
                    bullish_score=sent_result["bullish_score"],
                    bearish_score=sent_result["bearish_score"],
                    neutral_score=sent_result["neutral_score"],
                    composite_score=sent_result["composite_score"],
                )
                stored += 1

        return stored
