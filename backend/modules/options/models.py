"""
File path: backend/modules/options/models.py
Purpose: SQLAlchemy models for options market data.
         Tables: options_snapshots, vix_data. Per SPEC Section 10.2.
"""
import uuid
from datetime import datetime, date
from sqlalchemy import Column, String, Float, Integer, DateTime, Date, JSON
from sqlalchemy.dialects.sqlite import TEXT
try:
    from core.database import Base
except ImportError:
    from sqlalchemy.orm import declarative_base; Base = declarative_base()

class OptionsSnapshot(Base):
    """Options chain snapshot for a symbol at a given datetime."""
    __tablename__ = "options_snapshots"
    id = Column(TEXT, primary_key=True, default=lambda: str(uuid.uuid4()))
    symbol = Column(String(20), nullable=False, index=True)
    snapshot_at = Column(DateTime, nullable=False, index=True)
    expiry_date = Column(Date, nullable=False)
    strike = Column(Float, nullable=False)
    option_type = Column(String(4), nullable=False)     # call | put
    bid = Column(Float, nullable=True)
    ask = Column(Float, nullable=True)
    last_price = Column(Float, nullable=True)
    volume = Column(Integer, nullable=True)
    open_interest = Column(Integer, nullable=True)
    implied_volatility = Column(Float, nullable=True)   # decimal, e.g. 0.25 = 25%
    delta = Column(Float, nullable=True)
    gamma = Column(Float, nullable=True)
    theta = Column(Float, nullable=True)
    vega = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class VIXData(Base):
    """VIX term structure snapshot (spot + futures)."""
    __tablename__ = "vix_data"
    id = Column(TEXT, primary_key=True, default=lambda: str(uuid.uuid4()))
    snapshot_at = Column(DateTime, nullable=False, index=True)
    vix_9d = Column(Float, nullable=True)
    vix_spot = Column(Float, nullable=True)
    vix_3m = Column(Float, nullable=True)
    vix_6m = Column(Float, nullable=True)
    term_structure = Column(String(15), nullable=True)  # contango | backwardation | flat
    created_at = Column(DateTime, default=datetime.utcnow)
