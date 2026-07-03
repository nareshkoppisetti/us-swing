"""
File path: backend/modules/signals/models.py
Purpose: SQLAlchemy model for trading signals derived from predictions.
         Table: signals. Per SPEC Section 10.2.

IMPORTANT: This model is named TradeSignal (not Signal) to avoid a name clash
           with the Signal enum defined in modules/agents/base_agent.py.
           The database table name remains "signals".
"""
import uuid
from datetime import datetime, date
from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, Date, ForeignKey
from sqlalchemy.dialects.sqlite import TEXT
try:
    from core.database import Base
except ImportError:
    from sqlalchemy.orm import declarative_base; Base = declarative_base()


class TradeSignal(Base):
    """
    Tradeable signal derived from a Prediction when confidence >= threshold.
    Renamed from Signal to TradeSignal to avoid clash with agents.base_agent.Signal enum.
    """
    __tablename__ = "signals"

    id = Column(TEXT, primary_key=True, default=lambda: str(uuid.uuid4()))
    prediction_id = Column(TEXT, ForeignKey("predictions.id"), nullable=False, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    signal_date = Column(Date, nullable=False, index=True)
    direction = Column(String(10), nullable=False)        # Bullish | Bearish
    horizon_days = Column(Integer, nullable=False)
    confidence_score = Column(Float, nullable=False)
    risk_score = Column(Float, nullable=False)
    suggested_entry = Column(Float, nullable=True)
    suggested_stop = Column(Float, nullable=True)
    suggested_target_1 = Column(Float, nullable=True)
    suggested_target_2 = Column(Float, nullable=True)
    risk_reward_ratio = Column(Float, nullable=True)
    is_active = Column(Boolean, default=True)
    invalidated_at = Column(DateTime, nullable=True)
    invalidation_reason = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
