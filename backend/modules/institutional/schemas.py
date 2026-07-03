"""
File path: backend/modules/institutional/schemas.py
Purpose: Pydantic schemas for institutional flow API responses.
"""
from datetime import date, datetime
from pydantic import BaseModel

class InstitutionalFlowOut(BaseModel):
    id: str; symbol: str; flow_date: date; net_flow_usd: float | None
    buy_volume: int | None; sell_volume: int | None; source: str; created_at: datetime
    class Config: from_attributes = True

class DarkPoolActivityOut(BaseModel):
    id: str; symbol: str; week_ending: date; ats_volume: int | None
    ats_share_pct: float | None; is_degraded: bool; created_at: datetime
    class Config: from_attributes = True

class InsiderTransactionOut(BaseModel):
    id: str; symbol: str; transaction_date: date; insider_name: str | None
    insider_role: str | None; transaction_type: str; shares: int | None
    price_per_share: float | None; total_value: float | None; created_at: datetime
    class Config: from_attributes = True

class ThirteenFHoldingOut(BaseModel):
    id: str; symbol: str; institution_name: str; quarter_end: date
    shares_held: int | None; market_value_usd: float | None
    pct_of_portfolio: float | None; change_from_prior: int | None
    class Config: from_attributes = True
