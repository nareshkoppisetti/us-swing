"""
File: backend/modules/news/service.py
Purpose: NewsService — DB query layer for news articles and sentiment.
         Production implementation of the Phase 3 stub.

Responsibilities:
  - get_articles(symbol, hours, limit) → list[dict]
  - get_sentiment_summary(symbol, hours) → dict
  - get_high_impact(symbol, limit) → list[dict]
  - store_article(...) → NewsArticle ORM object
  - store_sentiment(...) → NewsSentiment ORM object

Per SPEC Section 9.2 and SPEC Section 10.2 (DB schema).
"""
import logging
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import desc, func

from modules.news.models import NewsArticle, NewsSentiment

logger = logging.getLogger("app")


class NewsService:
    def __init__(self, db: Session):
        self.db = db

    # ── Retrieval ─────────────────────────────────────────────────────────────

    def get_articles(
        self,
        symbol: str = None,
        hours: int = 24,
        limit: int = 50,
        sentiment_filter: str = None,   # "bullish" | "bearish" | "neutral" | None
    ) -> list[dict]:
        """
        Return recent news articles, optionally filtered by symbol.
        Ordered by published_at DESC.
        sentiment_filter: if provided, filter by composite_score thresholds.
        """
        since = datetime.utcnow() - timedelta(hours=hours)
        try:
            q = self.db.query(NewsArticle, NewsSentiment).outerjoin(
                NewsSentiment, NewsSentiment.article_id == NewsArticle.id
            ).filter(NewsArticle.published_at >= since)

            if symbol:
                # Filter by JSON array containing symbol
                # SQLite: use JSON1 extension; fallback: LIKE search
                q = q.filter(
                    func.json_each(NewsArticle.symbols).c.value == symbol.upper()
                )

            if sentiment_filter == "bullish":
                q = q.filter(NewsSentiment.composite_score > 0.05)
            elif sentiment_filter == "bearish":
                q = q.filter(NewsSentiment.composite_score < -0.05)
            elif sentiment_filter == "neutral":
                q = q.filter(
                    NewsSentiment.composite_score >= -0.05,
                    NewsSentiment.composite_score <= 0.05,
                )

            rows = q.order_by(desc(NewsArticle.published_at)).limit(limit).all()
            return [self._serialize(article, sent) for article, sent in rows]

        except Exception as e:
            # JSON1 may not be available — fallback to simple query
            logger.warning(f"get_articles advanced query failed, using simple: {e}")
            try:
                q = self.db.query(NewsArticle).filter(
                    NewsArticle.published_at >= since
                ).order_by(desc(NewsArticle.published_at)).limit(limit)
                return [self._serialize(a, None) for a in q.all()]
            except Exception as e2:
                logger.error(f"get_articles fallback failed: {e2}")
                return []

    def get_sentiment_summary(self, symbol: str, hours: int = 24) -> dict:
        """
        Aggregate NewsSentiment rows for symbol over N hours.
        Returns comprehensive sentiment summary used by Agent 7.
        """
        since = datetime.utcnow() - timedelta(hours=hours)
        try:
            rows = (
                self.db.query(NewsSentiment, NewsArticle)
                .join(NewsArticle, NewsArticle.id == NewsSentiment.article_id)
                .filter(
                    NewsSentiment.symbol == symbol.upper(),
                    NewsArticle.published_at >= since,
                )
                .order_by(desc(NewsArticle.published_at))
                .limit(50)
                .all()
            )

            if not rows:
                return {
                    "symbol": symbol,
                    "period_hours": hours,
                    "composite_score": 0.0,
                    "bullish_count": 0,
                    "bearish_count": 0,
                    "neutral_count": 0,
                    "article_count": 0,
                    "top_headlines": [],
                }

            composites, bullish_c, bearish_c, neutral_c = [], 0, 0, 0
            headlines = []
            for sent, article in rows:
                composites.append(sent.composite_score)
                if sent.composite_score > 0.05:
                    bullish_c += 1
                elif sent.composite_score < -0.05:
                    bearish_c += 1
                else:
                    neutral_c += 1
                if len(headlines) < 5:
                    headlines.append(article.headline)

            composite_avg = sum(composites) / len(composites) if composites else 0.0

            return {
                "symbol": symbol,
                "period_hours": hours,
                "composite_score": round(composite_avg, 4),
                "bullish_count": bullish_c,
                "bearish_count": bearish_c,
                "neutral_count": neutral_c,
                "article_count": len(rows),
                "top_headlines": headlines,
            }
        except Exception as e:
            logger.error(f"get_sentiment_summary failed for {symbol}: {e}")
            return {
                "symbol": symbol, "period_hours": hours,
                "composite_score": 0.0, "bullish_count": 0,
                "bearish_count": 0, "neutral_count": 0,
                "article_count": 0, "top_headlines": [],
            }

    def get_high_impact(self, symbol: str = None, limit: int = 20) -> list[dict]:
        """Return articles with highest |impact_score|."""
        try:
            q = self.db.query(NewsArticle)
            if symbol:
                # Approximate JSON filter
                q = q.filter(NewsArticle.symbols.contains(symbol.upper()))
            rows = (
                q.filter(NewsArticle.impact_score.isnot(None))
                .order_by(desc(NewsArticle.impact_score))
                .limit(limit)
                .all()
            )
            return [self._serialize(a, None) for a in rows]
        except Exception as e:
            logger.error(f"get_high_impact failed: {e}")
            return []

    def get_economic_calendar(self) -> list[dict]:
        """Return upcoming economic events (hardcoded + any stored events)."""
        from modules.news.economic_calendar import get_upcoming_events
        return get_upcoming_events()

    # ── Storage ───────────────────────────────────────────────────────────────

    def store_article(
        self,
        headline: str,
        source: str,
        url: str,
        published_at: datetime,
        symbols: list,
        sentiment_score: float = None,
        impact_score: float = None,
    ) -> NewsArticle:
        """
        Insert a NewsArticle record.
        Deduplicates by URL — returns existing if already stored.
        """
        try:
            existing = self.db.query(NewsArticle).filter_by(url=url).first()
            if existing:
                return existing

            article = NewsArticle(
                headline=headline[:500],
                source=source[:100],
                url=url[:1000],
                published_at=published_at,
                symbols=[s.upper() for s in (symbols or [])],
                sentiment_score=sentiment_score,
                impact_score=impact_score,
            )
            self.db.add(article)
            self.db.flush()  # get ID without full commit
            return article
        except Exception as e:
            logger.error(f"store_article failed for '{headline[:60]}': {e}")
            self.db.rollback()
            return None

    def store_sentiment(
        self,
        article_id: str,
        symbol: str,
        bullish_score: float,
        bearish_score: float,
        neutral_score: float,
        composite_score: float,
    ) -> NewsSentiment:
        """Insert or update a NewsSentiment record."""
        try:
            # Upsert: delete + insert (simpler than merge for SQLite)
            existing = self.db.query(NewsSentiment).filter_by(
                article_id=article_id, symbol=symbol.upper()
            ).first()
            if existing:
                existing.bullish_score = bullish_score
                existing.bearish_score = bearish_score
                existing.neutral_score = neutral_score
                existing.composite_score = composite_score
                existing.analyzed_at = datetime.utcnow()
                return existing

            sent = NewsSentiment(
                article_id=article_id,
                symbol=symbol.upper(),
                bullish_score=bullish_score,
                bearish_score=bearish_score,
                neutral_score=neutral_score,
                composite_score=composite_score,
            )
            self.db.add(sent)
            self.db.flush()
            return sent
        except Exception as e:
            logger.error(f"store_sentiment failed: {e}")
            self.db.rollback()
            return None

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _serialize(self, article: NewsArticle, sentiment: NewsSentiment) -> dict:
        """Convert ORM row pair to dict for API response."""
        sent_map = (
            article.sentiment_score  # fallback if no sentiment row
            if sentiment is None
            else sentiment.composite_score
        )
        return {
            "id": article.id,
            "headline": article.headline,
            "title": article.headline,          # alias for frontend compat
            "source": article.source,
            "url": article.url,
            "published_at": article.published_at.isoformat() if article.published_at else None,
            "created_at": article.created_at.isoformat() if article.created_at else None,
            "symbols": article.symbols or [],
            "impact_score": article.impact_score,
            "sentiment_score": sent_map,
            "sentiment": _score_to_label(sent_map),
            "bullish_score": sentiment.bullish_score if sentiment else None,
            "bearish_score": sentiment.bearish_score if sentiment else None,
        }


def _score_to_label(score: float) -> str:
    if score is None:
        return "neutral"
    if score > 0.05:
        return "bullish"
    if score < -0.05:
        return "bearish"
    return "neutral"
