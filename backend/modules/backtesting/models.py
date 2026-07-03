"""
File path: backend/modules/backtesting/models.py
Purpose: SQLAlchemy models for backtesting framework.
         Tables: backtests, backtest_results. Per SPEC Section 10.2 and FR-003.
"""
import uuid
from datetime import datetime, date
from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, Date, JSON
from sqlalchemy.dialects.sqlite import TEXT
try:
    from core.database import Base
except ImportError:
    from sqlalchemy.orm import declarative_base; Base = declarative_base()

class Backtest(Base):
    """A backtest run configuration."""
    __tablename__ = "backtests"
    id = Column(TEXT, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    symbol = Column(String(20), nullable=False, index=True)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    horizon_days = Column(Integer, nullable=False)
    confidence_threshold = Column(Float, nullable=False, default=65.0)
    model_version = Column(String(50), nullable=True)
    status = Column(String(20), default="pending")  # pending | running | complete | failed
    triggered_by = Column(String(50), nullable=True)  # scheduler | manual
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

class BacktestResult(Base):
    """Aggregated performance metrics for a backtest run."""
    __tablename__ = "backtest_results"
    id = Column(TEXT, primary_key=True, default=lambda: str(uuid.uuid4()))
    backtest_id = Column(TEXT, nullable=False, index=True)
    total_predictions = Column(Integer, nullable=True)
    correct_predictions = Column(Integer, nullable=True)
    accuracy_pct = Column(Float, nullable=True)
    bullish_accuracy_pct = Column(Float, nullable=True)
    bearish_accuracy_pct = Column(Float, nullable=True)
    avg_confidence = Column(Float, nullable=True)
    calibration_error = Column(Float, nullable=True)   # |predicted_conf - actual_accuracy|
    sharpe_ratio = Column(Float, nullable=True)
    max_drawdown_pct = Column(Float, nullable=True)
    total_return_pct = Column(Float, nullable=True)
    win_rate_pct = Column(Float, nullable=True)
    avg_win_pct = Column(Float, nullable=True)
    avg_loss_pct = Column(Float, nullable=True)
    by_horizon = Column(JSON, nullable=True)           # {2: {...}, 5: {...}, ...}
    by_sector = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
