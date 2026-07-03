"""Agent 07 — News Analyst | News & Macro | Tier 1
Fetches and scores news sentiment for a symbol.
Primary: reads from NewsIntelligenceEngine DB cache.
Fallback: direct collector calls (Yahoo + NewsAPI).
Per SPEC BUILD_PLAN Phase 5.
"""
import time
import logging
import numpy as np
from datetime import datetime
from modules.agents.base_agent import BaseAgent, AgentOutput, Signal

logger = logging.getLogger("agents")


class Agent07(BaseAgent):
    agent_id = 7
    agent_name = "News Analyst"
    category = "News & Macro"
    refresh_frequency = "30min"
    dependencies = []
    tier = 1

    def run(self, symbol, context):
        start = time.time()
        try:
            articles = []
            composite = 0.0
            bull_count = bear_count = 0
            top_headline = ""
            source_used = "direct"

            # ── Path 1: NewsIntelligenceEngine DB (preferred) ────────────────
            try:
                from modules.news.engine import NewsIntelligenceEngine
                engine = NewsIntelligenceEngine(db=None)
                summary = engine.get_symbol_sentiment(symbol, hours=24)
                if summary.get("article_count", 0) > 0:
                    composite = summary["composite_score"]
                    bull_count = summary["bullish_count"]
                    bear_count = summary["bearish_count"]
                    top_headline = (summary.get("top_headlines") or [""])[0]
                    article_count = summary["article_count"]
                    source_used = "engine"
            except Exception as e:
                logger.debug(f"Agent07: engine path failed ({e}), using collectors")

            # ── Path 2: Direct collector fallback ────────────────────────────
            if source_used == "direct":
                from modules.market_data.collectors.yahoo_collector import YahooFinanceCollector
                yc = YahooFinanceCollector()
                raw = yc.fetch_news(symbol, limit=20)
                articles = [{"title": a.get("title", ""), "content": a.get("summary", "")}
                            for a in raw]

                try:
                    from modules.market_data.collectors.newsapi_collector import NewsAPICollector
                    nc = NewsAPICollector()
                    raw2 = nc.fetch_news(symbol, limit=20)
                    articles += [{"title": a.get("title", ""), "content": a.get("content", "")}
                                 for a in raw2]
                except Exception:
                    pass

                if not articles:
                    return AgentOutput(
                        agent_id=self.agent_id, agent_name=self.agent_name,
                        signal=Signal.NEUTRAL, score=50.0, confidence=20.0, weight=0.7,
                        reasoning="No news articles available",
                        bullish_factors=[], bearish_factors=[],
                        supporting_data={
                            "composite_sentiment": 0.0, "bull_articles": 0,
                            "bear_articles": 0, "article_count": 0, "top_headline": "",
                        },
                        llm_ready_summary={"agent": self.agent_name, "signal": "Neutral",
                                           "finding": "No news data"},
                        data_freshness=datetime.utcnow().isoformat(),
                        execution_time_ms=int((time.time() - start) * 1000),
                    )

                # Score with SentimentAnalyzer
                from modules.news.sentiment import SentimentAnalyzer
                analyzer = SentimentAnalyzer()
                scored = analyzer.analyze_batch(articles)
                composites = [s["composite_score"] for s in scored]
                composite = float(np.mean(composites)) if composites else 0.0
                bull_count = sum(1 for s in composites if s > 0.05)
                bear_count = sum(1 for s in composites if s < -0.05)
                top_headline = articles[0].get("title", "") if articles else ""
                article_count = len(articles)

            # ── Signal generation ────────────────────────────────────────────
            news_score = float(np.clip(50 + composite * 40, 0, 100))
            signal = (Signal.BULLISH if news_score >= 58
                      else Signal.BEARISH if news_score <= 42
                      else Signal.NEUTRAL)
            article_count = article_count if source_used == "direct" else summary.get("article_count", 0)
            conf = float(np.clip(30 + article_count * 1.5 + abs(composite) * 30, 0, 80))

            bullish_factors = [f"{bull_count} bullish articles"] if bull_count > bear_count else []
            bearish_factors = [f"{bear_count} bearish articles"] if bear_count > bull_count else []
            if abs(composite) > 0.4:
                intensity = "strongly" if abs(composite) > 0.6 else "moderately"
                if composite > 0:
                    bullish_factors.append(f"News sentiment {intensity} positive (score {composite:.2f})")
                else:
                    bearish_factors.append(f"News sentiment {intensity} negative (score {composite:.2f})")

            return AgentOutput(
                agent_id=self.agent_id,
                agent_name=self.agent_name,
                signal=signal,
                score=news_score,
                confidence=conf,
                weight=0.7,
                reasoning=(
                    f"Sentiment composite={composite:.3f} from {article_count} articles. "
                    f"Bull:{bull_count}, Bear:{bear_count}. Source={source_used}"
                ),
                bullish_factors=bullish_factors,
                bearish_factors=bearish_factors,
                supporting_data={
                    "composite_sentiment": round(composite, 4),
                    "bull_articles": bull_count,
                    "bear_articles": bear_count,
                    "article_count": article_count,
                    "top_headline": top_headline[:150],
                    "news_score": news_score,
                },
                llm_ready_summary={
                    "agent": self.agent_name,
                    "signal": signal.value,
                    "finding": (
                        f"Sentiment={composite:.3f}; bull={bull_count} bear={bear_count} "
                        f"of {article_count} articles; top: {top_headline[:80]}"
                    ),
                },
                data_freshness=datetime.utcnow().isoformat(),
                execution_time_ms=int((time.time() - start) * 1000),
            )

        except Exception as e:
            logger.error(f"Agent07 failed: {e}")
            return AgentOutput(
                agent_id=self.agent_id, agent_name=self.agent_name,
                signal=Signal.NEUTRAL, score=50.0, confidence=0.0, weight=0.7,
                reasoning="", bullish_factors=[], bearish_factors=[],
                supporting_data={},
                llm_ready_summary={"agent": self.agent_name, "signal": "Neutral", "finding": "Failed"},
                data_freshness="",
                execution_time_ms=int((time.time() - start) * 1000),
                error=str(e),
            )
