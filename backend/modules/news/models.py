"""
File path: backend/modules/news/models.py
Purpose: SQLAlchemy models for news articles and sentiment scores.
         Tables: news_articles, news_sentiment. Per SPEC Section 10.2.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, JSON, ForeignKey
from sqlalchemy.dialects.sqlite import TEXT
try:
    from core.database import Base
except ImportError:
    from sqlalchemy.orm import declarative_base; Base = declarative_base()

class NewsArticle(Base):
    __tablename__ = "news_articles"
    id = Column(TEXT, primary_key=True, default=lambda: str(uuid.uuid4()))
    headline = Column(String(500), nullable=False)
    source = Column(String(100), nullable=False)
    url = Column(String(1000), unique=True, nullable=False)
    published_at = Column(DateTime, nullable=False, index=True)
    symbols = Column(JSON, nullable=True)     # list of related tickers
    impact_score = Column(Float, nullable=True)
    sentiment_score = Column(Float, nullable=True)  # -1.0 to +1.0
    created_at = Column(DateTime, default=datetime.utcnow)

class NewsSentiment(Base):
    __tablename__ = "news_sentiment"
    id = Column(TEXT, primary_key=True, default=lambda: str(uuid.uuid4()))
    article_id = Column(TEXT, ForeignKey("news_articles.id"), nullable=False, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    bullish_score = Column(Float, nullable=False, default=0.0)
    bearish_score = Column(Float, nullable=False, default=0.0)
    neutral_score = Column(Float, nullable=False, default=0.0)
    composite_score = Column(Float, nullable=False, default=0.0)  # -1.0 to +1.0
    analyzed_at = Column(DateTime, default=datetime.utcnow)
