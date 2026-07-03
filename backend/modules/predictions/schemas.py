"""
File path: backend/modules/predictions/schemas.py
Purpose: Pydantic schemas for predictions API. Per SPEC FR-002.
"""
from datetime import datetime, date
from pydantic import BaseModel

class PredictionOut(BaseModel):
    id: str
    symbol: str
    prediction_date: date
    horizon_days: int
    direction: str
    confidence_score: float
    risk_score: float
    expected_move_pct: float | None
    expiry_date: date
    actual_direction: str | None
    is_correct: bool | None
    status: str
    created_at: datetime
    class Config: from_attributes = True

class PredictionRequest(BaseModel):
    symbol: str
    horizons: list[int] = [2, 5, 10, 20, 30, 60]
