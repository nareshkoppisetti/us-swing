"""
File path: backend/modules/performance/models.py
Purpose: SQLAlchemy model for ongoing prediction performance tracking.
         Table: prediction_performance. Per SPEC Section 10.2.
         
Unlike backtesting (historical replay), this tracks live prediction accuracy
as predictions expire and are resolved against actual market data.
"""
import uuid
from datetime import datetime, date
from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, Date, ForeignKey
from sqlalchemy.dialects.sqlite import TEXT
try:
    from core.database import Base
except ImportError:
    from sqlalchemy.orm import declarative_base; Base = declarative_base()

class PredictionPerformance(Base):
    """Records actual outcome vs prediction for each expired prediction."""
    __tablename__ = "prediction_performance"
    id = Column(TEXT, primary_key=True, default=lambda: str(uuid.uuid4()))
    prediction_id = Column(TEXT, ForeignKey("predictions.id"), unique=True, nullable=False, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    horizon_days = Column(Integer, nullable=False)
    predicted_direction = Column(String(10), nullable=False)
    actual_direction = Column(String(10), nullable=False)
    is_correct = Column(Boolean, nullable=False)
    predicted_confidence = Column(Float, nullable=False)
    predicted_move_pct = Column(Float, nullable=True)
    actual_move_pct = Column(Float, nullable=True)        # actual % change at expiry
    entry_price = Column(Float, nullable=True)            # close on prediction date
    exit_price = Column(Float, nullable=True)             # close on expiry date
    resolved_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
