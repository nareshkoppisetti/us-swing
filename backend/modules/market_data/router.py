"""
File path: backend/modules/market_data/router.py
Purpose: FastAPI router for market data endpoints.
         Registered at prefix /api/v1/market in main.py (no prefix here per BUILD_PLAN Rule 10).

Endpoints:
  GET /market/ohlcv/{symbol}        — fetch OHLCV for a symbol
  GET /market/quote/{symbol}        — current quote
  GET /market/indicators/{symbol}   — technical indicators
  GET /market/regime                — current market regime (Agent 1 output)
"""
import logging
from datetime import datetime
from uuid import uuid4

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from dependencies import get_db, get_current_user
from modules.market_data.service import MarketDataService
from modules.market_data.schemas import OHLCVResponse, OHLCVBar, MarketIndicatorsResponse

logger = logging.getLogger("app")

router = APIRouter(tags=["Market Data"])


def _build_meta() -> dict:
    return {"request_id": str(uuid4()), "timestamp": datetime.utcnow().isoformat() + "Z", "version": "1.0"}


@router.get("/ohlcv/{symbol}")
def get_ohlcv(
    symbol: str,
    timeframe: str = Query("daily", description="daily | weekly | monthly"),
    period: str = Query("1y", description="1d | 5d | 1mo | 3mo | 6mo | 1y | 2y | 5y"),
    days: int = Query(None, description="Alternative to period: number of calendar days"),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    """
    Fetch OHLCV bars for a symbol.
    Falls back to live Yahoo Finance fetch if Parquet missing.
    """
    try:
        svc = MarketDataService(db=db)
        df = svc.get_ohlcv(symbol.upper(), timeframe=timeframe, period=period, days=days)

        bars = []
        for _, row in df.iterrows():
            bars.append(OHLCVBar(
                date=row["date"],
                open=float(row.get("open", 0) or 0),
                high=float(row.get("high", 0) or 0),
                low=float(row.get("low", 0) or 0),
                close=float(row.get("close", 0) or 0),
                volume=int(row.get("volume", 0) or 0),
                vwap=float(row["vwap"]) if row.get("vwap") is not None else None,
            ))

        return {
            "success": True,
            "data": OHLCVResponse(
                symbol=symbol.upper(),
                timeframe=timeframe,
                bars=bars,
                source="market_data_service",
                fetched_at=datetime.utcnow().isoformat() + "Z",
            ).model_dump(),
            "meta": _build_meta(),
        }
    except Exception as e:
        logger.error(f"GET /market/ohlcv/{symbol}: {e}")
        raise HTTPException(status_code=503, detail=str(e))


@router.get("/quote/{symbol}")
def get_quote(
    symbol: str,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    """Return current market quote for symbol."""
    try:
        svc = MarketDataService(db=db)
        quote = svc.get_quote(symbol.upper())
        return {"success": True, "data": quote, "meta": _build_meta()}
    except Exception as e:
        logger.error(f"GET /market/quote/{symbol}: {e}")
        raise HTTPException(status_code=503, detail=str(e))


@router.get("/indicators/{symbol}")
def get_indicators(
    symbol: str,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    """Return computed technical indicators for a symbol."""
    try:
        svc = MarketDataService(db=db)
        indicators = svc.get_indicators(symbol.upper())
        return {"success": True, "data": indicators, "meta": _build_meta()}
    except Exception as e:
        logger.error(f"GET /market/indicators/{symbol}: {e}")
        raise HTTPException(status_code=503, detail=str(e))


@router.get("/regime")
def get_regime(
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    """Return current market regime from Agent 1's most recent output for SPY."""
    try:
        svc = MarketDataService(db=db)
        regime = svc.get_market_regime(db=db)
        return {"success": True, "data": regime, "meta": _build_meta()}
    except Exception as e:
        logger.error(f"GET /market/regime: {e}")
        raise HTTPException(status_code=503, detail=str(e))
