"""
File path: backend/modules/backtesting/schemas.py
Purpose: Pydantic schemas for backtesting API.
"""
from datetime import date, datetime
from pydantic import BaseModel

class BacktestRequest(BaseModel):
    symbol: str
    start_date: date
    end_date: date
    horizon_days: int = 10
    confidence_threshold: float = 65.0

class BacktestOut(BaseModel):
    id: str; name: str; symbol: str; start_date: date; end_date: date
    horizon_days: int; status: str; created_at: datetime; completed_at: datetime | None
    class Config: from_attributes = True

class BacktestResultOut(BaseModel):
    id: str; backtest_id: str; total_predictions: int | None
    correct_predictions: int | None; accuracy_pct: float | None
    bullish_accuracy_pct: float | None; bearish_accuracy_pct: float | None
    avg_confidence: float | None; calibration_error: float | None
    sharpe_ratio: float | None; max_drawdown_pct: float | None
    total_return_pct: float | None; win_rate_pct: float | None
    by_horizon: dict | None; created_at: datetime
    class Config: from_attributes = True
