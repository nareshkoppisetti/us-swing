"""
File path: backend/modules/predictions/models.py
Purpose: SQLAlchemy models for predictions, prediction reasons, and contributors.
         Tables: predictions, prediction_reasons, prediction_contributors
         Per SPEC Section 10.2.
"""
import uuid
from datetime import datetime, date
from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, Date, JSON, Enum, ForeignKey
from sqlalchemy.dialects.sqlite import TEXT
from sqlalchemy.orm import relationship
try:
    from core.database import Base
except ImportError:
    from sqlalchemy.orm import declarative_base; Base = declarative_base()

class Prediction(Base):
    __tablename__ = "predictions"
    id = Column(TEXT, primary_key=True, default=lambda: str(uuid.uuid4()))
    symbol = Column(String(20), nullable=False, index=True)
    prediction_date = Column(Date, nullable=False)
    horizon_days = Column(Integer, nullable=False)  # 2|5|10|20|30|60
    direction = Column(Enum("Bullish","Bearish","Neutral"), nullable=False)
    confidence_score = Column(Float, nullable=False)
    risk_score = Column(Float, nullable=False)
    expected_move_pct = Column(Float, nullable=True)
    expiry_date = Column(Date, nullable=False)
    actual_direction = Column(String(10), nullable=True)  # filled on expiry
    is_correct = Column(Boolean, nullable=True)
    status = Column(Enum("active","expired","superseded"), default="active")
    agent_run_id = Column(TEXT, nullable=True)
    model_version = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class PredictionReason(Base):
    __tablename__ = "prediction_reasons"
    id = Column(TEXT, primary_key=True, default=lambda: str(uuid.uuid4()))
    prediction_id = Column(TEXT, ForeignKey("predictions.id"), nullable=False, index=True)
    factor_type = Column(Enum("bullish","bearish"), nullable=False)
    factor = Column(String(500), nullable=False)
    supporting_data = Column(String(1000), nullable=True)
    agent_id = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class PredictionContributor(Base):
    __tablename__ = "prediction_contributors"
    id = Column(TEXT, primary_key=True, default=lambda: str(uuid.uuid4()))
    prediction_id = Column(TEXT, ForeignKey("predictions.id"), nullable=False, index=True)
    agent_id = Column(Integer, nullable=False)
    agent_name = Column(String(100), nullable=False)
    signal = Column(String(10), nullable=False)
    score = Column(Float, nullable=False)
    weight = Column(Float, nullable=False)
    impact = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
