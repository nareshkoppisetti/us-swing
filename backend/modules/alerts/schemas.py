"""
File path: backend/modules/alerts/schemas.py
Purpose: Pydantic schemas for alerts API.
"""
from datetime import datetime
from pydantic import BaseModel

class AlertCreate(BaseModel):
    symbol: str
    alert_type: str
    threshold_value: float | None = None
    direction_filter: str | None = None
    horizon_filter: str | None = None
    notify_email: bool = True
    notify_in_app: bool = True

class AlertOut(BaseModel):
    id: str; user_id: str; symbol: str; alert_type: str
    threshold_value: float | None; direction_filter: str | None
    is_active: bool; notify_email: bool; notify_in_app: bool
    last_triggered_at: datetime | None; trigger_count: float
    created_at: datetime
    class Config: from_attributes = True
