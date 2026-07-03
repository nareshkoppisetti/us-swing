"""
File: backend/modules/news/router.py
Purpose: News Intelligence REST endpoints.
         Production implementation replacing Phase 3 stub.

Endpoints:
  GET  /news/              — list articles (filter by symbol, sentiment, limit)
  GET  /news/sentiment/{symbol} — aggregated sentiment summary
  GET  /news/economic-calendar  — upcoming high-impact events
  POST /news/fetch         — trigger live fetch + store for watchlist
"""
import logging
from datetime import datetime
from uuid import uuid4

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from dependencies import get_db, get_current_user
from modules.news.service import NewsService
from modules.news.engine import NewsIntelligenceEngine
from modules.news.economic_calendar import get_upcoming_events

logger = logging.getLogger("app")
router = APIRouter(tags=["News"])


def _meta():
    return {"request_id": str(uuid4()), "timestamp": datetime.utcnow().isoformat() + "Z"}


@router.get("/")
def list_news(
    symbol: str = Query(None, description="Filter by ticker symbol"),
    sentiment: str = Query(None, description="bullish | bearish | neutral"),
    limit: int = Query(50, ge=1, le=200),
    hours: int = Query(48, ge=1, le=720),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    """Return recent news articles with sentiment scores."""
    try:
        svc = NewsService(db)
        articles = svc.get_articles(
            symbol=symbol,
            hours=hours,
            limit=limit,
            sentiment_filter=sentiment,
        )
        return {
            "success": True,
            "data": articles,
            "meta": {**_meta(), "count": len(articles), "symbol": symbol, "hours": hours},
        }
    except Exception as e:
        logger.error(f"GET /news/ failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sentiment/{symbol}")
def get_sentiment(
    symbol: str,
    hours: int = Query(24, ge=1, le=168),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    """Aggregated sentiment summary for a symbol over N hours."""
    try:
        svc = NewsService(db)
        summary = svc.get_sentiment_summary(symbol.upper(), hours=hours)
        return {"success": True, "data": summary, "meta": _meta()}
    except Exception as e:
        logger.error(f"GET /news/sentiment/{symbol} failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/economic-calendar")
def economic_calendar(_=Depends(get_current_user)):
    """Return upcoming high-impact economic events."""
    try:
        events = get_upcoming_events(days_ahead=45)
        return {"success": True, "data": events, "meta": _meta()}
    except Exception as e:
        logger.error(f"GET /news/economic-calendar failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/fetch")
def fetch_news(
    symbols: list[str] = None,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    """Trigger live news fetch + sentiment scoring + DB storage."""
    try:
        engine = NewsIntelligenceEngine(db=db)
        results = engine.run(symbols=symbols)
        total_articles = sum(v.get("article_count", 0) for v in results.values())
        return {
            "success": True,
            "data": {
                "symbols_processed": len(results),
                "total_articles_stored": total_articles,
                "per_symbol": results,
            },
            "meta": _meta(),
        }
    except Exception as e:
        logger.error(f"POST /news/fetch failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/high-impact")
def high_impact_news(
    symbol: str = Query(None),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    """Return articles with highest impact scores."""
    try:
        svc = NewsService(db)
        articles = svc.get_high_impact(symbol=symbol, limit=limit)
        return {"success": True, "data": articles, "meta": _meta()}
    except Exception as e:
        logger.error(f"GET /news/high-impact failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
