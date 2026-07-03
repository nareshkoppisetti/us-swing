"""
File path: backend/modules/options/schemas.py
Purpose: Pydantic schemas for options intelligence API responses.
"""
from datetime import datetime, date
from pydantic import BaseModel

class OptionsChainRow(BaseModel):
    expiry_date: date; strike: float; option_type: str
    bid: float | None; ask: float | None; volume: int | None
    open_interest: int | None; implied_volatility: float | None
    delta: float | None; gamma: float | None

class GammaExposureOut(BaseModel):
    symbol: str; snapshot_at: datetime
    total_gex: float; gamma_flip_level: float | None
    by_strike: dict  # {strike_str: gex_value}

class VIXTermStructureOut(BaseModel):
    snapshot_at: datetime
    vix_9d: float | None; vix_spot: float | None
    vix_3m: float | None; vix_6m: float | None
    term_structure: str | None
