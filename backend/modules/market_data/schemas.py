"""
File path: backend/modules/market_data/schemas.py
Purpose: Pydantic schemas for market data API requests and responses.
"""

from datetime import date
from pydantic import BaseModel


class OHLCVBar(BaseModel):
    """Single OHLCV candlestick bar."""
    date: date
    open: float
    high: float
    low: float
    close: float
    volume: int
    vwap: float | None = None


class OHLCVResponse(BaseModel):
    """Response for GET /market/ohlcv?symbol=AAPL&timeframe=daily"""
    symbol: str
    timeframe: str  # daily | weekly | monthly
    bars: list[OHLCVBar]
    source: str
    fetched_at: str  # ISO timestamp


class MarketIndicatorsResponse(BaseModel):
    """Technical indicators computed from OHLCV data."""
    symbol: str
    date: date
    sma_20: float | None
    sma_50: float | None
    sma_200: float | None
    ema_12: float | None
    ema_26: float | None
    rsi_14: float | None
    adx_14: float | None
    atr_14: float | None
    macd: float | None
    macd_signal: float | None
    bb_upper: float | None
    bb_lower: float | None
    volume_sma_20: float | None
