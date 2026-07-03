"""
File path: backend/modules/signals/schemas.py
Purpose: Pydantic schemas for signals API.
         Note: ORM model is named TradeSignal (table: signals).
"""
from datetime import date, datetime
from pydantic import BaseModel


class SignalOut(BaseModel):
    id: str
    symbol: str
    signal_date: date
    direction: str
    horizon_days: int
    confidence_score: float
    risk_score: float
    suggested_entry: float | None
    suggested_stop: float | None
    suggested_target_1: float | None
    suggested_target_2: float | None
    risk_reward_ratio: float | None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
