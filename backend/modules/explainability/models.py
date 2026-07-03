"""
File path: backend/modules/explainability/models.py
Purpose: SQLAlchemy model for PredictionExplanation (LLM narratives).
         Table: prediction_explanations. Per SPEC Section 10.2.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, JSON, Enum, Integer, ForeignKey
from sqlalchemy.dialects.sqlite import TEXT
try:
    from core.database import Base
except ImportError:
    from sqlalchemy.orm import declarative_base; Base = declarative_base()

class PredictionExplanation(Base):
    __tablename__ = "prediction_explanations"
    id = Column(TEXT, primary_key=True, default=lambda: str(uuid.uuid4()))
    prediction_id = Column(TEXT, ForeignKey("predictions.id"), unique=True, nullable=False, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    horizon_days = Column(Integer, nullable=False)
    narrative_text = Column(String(2000), nullable=True)  # LLM-generated analyst narrative
    model_used = Column(String(100), nullable=True)       # e.g. "grok-beta"
    prompt_snapshot = Column(JSON, nullable=True)          # full prompt for auditability
    top_bullish_factors = Column(JSON, nullable=True)      # list of top 3 bullish data points
    top_bearish_factors = Column(JSON, nullable=True)      # list of top 3 bearish data points
    generation_status = Column(Enum("pending","complete","failed"), default="pending")
    fallback_used = Column(Boolean, default=False)
    generated_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
