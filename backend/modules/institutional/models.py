"""
File path: backend/modules/institutional/models.py
Purpose: SQLAlchemy models for institutional flow data.
         Tables: institutional_flows, dark_pool_activity, insider_transactions, thirteen_f_holdings
         Per SPEC Section 10.2.
"""
import uuid
from datetime import datetime, date
from sqlalchemy import Column, String, Float, Integer, BigInteger, Boolean, DateTime, Date, JSON
from sqlalchemy.dialects.sqlite import TEXT
try:
    from core.database import Base
except ImportError:
    from sqlalchemy.orm import declarative_base; Base = declarative_base()

class InstitutionalFlow(Base):
    """Aggregated institutional buy/sell flow per symbol per day."""
    __tablename__ = "institutional_flows"
    id = Column(TEXT, primary_key=True, default=lambda: str(uuid.uuid4()))
    symbol = Column(String(20), nullable=False, index=True)
    flow_date = Column(Date, nullable=False, index=True)
    net_flow_usd = Column(Float, nullable=True)          # positive = net buy
    buy_volume = Column(BigInteger, nullable=True)
    sell_volume = Column(BigInteger, nullable=True)
    source = Column(String(50), nullable=False)           # FINRA_ATS | proxy
    created_at = Column(DateTime, default=datetime.utcnow)

class DarkPoolActivity(Base):
    """Dark pool / ATS aggregate activity (weekly, FINRA aggregate only in MVP)."""
    __tablename__ = "dark_pool_activity"
    id = Column(TEXT, primary_key=True, default=lambda: str(uuid.uuid4()))
    symbol = Column(String(20), nullable=False, index=True)
    week_ending = Column(Date, nullable=False, index=True)
    ats_volume = Column(BigInteger, nullable=True)
    ats_share_pct = Column(Float, nullable=True)         # % of total volume
    source = Column(String(50), nullable=False)
    is_degraded = Column(Boolean, default=True)           # True = MVP aggregate mode
    created_at = Column(DateTime, default=datetime.utcnow)

class InsiderTransaction(Base):
    """SEC Form 4 insider transaction (purchase or sale)."""
    __tablename__ = "insider_transactions"
    id = Column(TEXT, primary_key=True, default=lambda: str(uuid.uuid4()))
    symbol = Column(String(20), nullable=False, index=True)
    transaction_date = Column(Date, nullable=False, index=True)
    insider_name = Column(String(255), nullable=True)
    insider_role = Column(String(100), nullable=True)
    transaction_type = Column(String(10), nullable=False)  # P (purchase) | S (sale)
    shares = Column(Integer, nullable=True)
    price_per_share = Column(Float, nullable=True)
    total_value = Column(Float, nullable=True)
    form4_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class ThirteenFHolding(Base):
    """SEC 13F quarterly institutional holding snapshot."""
    __tablename__ = "thirteen_f_holdings"
    id = Column(TEXT, primary_key=True, default=lambda: str(uuid.uuid4()))
    symbol = Column(String(20), nullable=False, index=True)
    institution_name = Column(String(255), nullable=False)
    quarter_end = Column(Date, nullable=False, index=True)
    shares_held = Column(BigInteger, nullable=True)
    market_value_usd = Column(Float, nullable=True)
    pct_of_portfolio = Column(Float, nullable=True)
    change_from_prior = Column(Integer, nullable=True)   # share delta vs last quarter
    created_at = Column(DateTime, default=datetime.utcnow)
