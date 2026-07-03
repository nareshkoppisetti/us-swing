"""
File path: backend/modules/explainability/schemas.py
Purpose: Pydantic schemas for explainability API.
"""
from datetime import datetime
from pydantic import BaseModel

class ExplanationOut(BaseModel):
    id: str
    prediction_id: str
    symbol: str
    horizon_days: int
    narrative_text: str | None
    model_used: str | None
    top_bullish_factors: list | None
    top_bearish_factors: list | None
    generation_status: str
    fallback_used: bool
    generated_at: datetime | None
    created_at: datetime
    class Config: from_attributes = True
