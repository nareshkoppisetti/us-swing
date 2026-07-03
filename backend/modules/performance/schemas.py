"""
File path: backend/modules/performance/schemas.py
Purpose: Pydantic schemas for performance tracking API.
"""
from datetime import datetime, date
from pydantic import BaseModel

class PerformanceRecordOut(BaseModel):
    id: str; symbol: str; horizon_days: int; predicted_direction: str
    actual_direction: str; is_correct: bool; predicted_confidence: float
    actual_move_pct: float | None; resolved_at: datetime
    class Config: from_attributes = True

class AccuracySummaryOut(BaseModel):
    total_predictions: int; correct_predictions: int; accuracy_pct: float
    bullish_accuracy_pct: float; bearish_accuracy_pct: float
    period_days: int; by_horizon: dict | None

class CalibrationReportOut(BaseModel):
    buckets: dict  # {"50-60": {predicted: 55, actual: 52.3, count: 142}, ...}
    overall_calibration_error: float
