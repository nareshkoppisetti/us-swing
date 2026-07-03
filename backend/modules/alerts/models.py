"""
File path: backend/modules/alerts/models.py
Purpose: SQLAlchemy model for user-configured price and signal alerts.
         Table: alerts. Per SPEC Section 10.2.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Boolean, DateTime, JSON, ForeignKey
from sqlalchemy.dialects.sqlite import TEXT
try:
    from core.database import Base
except ImportError:
    from sqlalchemy.orm import declarative_base; Base = declarative_base()

class Alert(Base):
    __tablename__ = "alerts"
    id = Column(TEXT, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(TEXT, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    alert_type = Column(String(30), nullable=False)
    # alert_type options:
    #   price_above | price_below
    #   new_prediction (any new prediction for symbol)
    #   confidence_above (prediction confidence > threshold)
    #   signal_generated (tradeable signal created)
    #   agent_failure (specific agent error rate > threshold)
    threshold_value = Column(Float, nullable=True)    # e.g. price level or confidence %
    direction_filter = Column(String(10), nullable=True)  # Bullish | Bearish | null (any)
    horizon_filter = Column(String(50), nullable=True)    # e.g. "5,10" or null (any)
    is_active = Column(Boolean, default=True)
    notify_email = Column(Boolean, default=True)
    notify_in_app = Column(Boolean, default=True)
    last_triggered_at = Column(DateTime, nullable=True)
    trigger_count = Column(Float, default=0)
    extra_data = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
