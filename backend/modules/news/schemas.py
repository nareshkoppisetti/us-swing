"""
File path: backend/modules/news/schemas.py
Purpose: Pydantic schemas for news API responses.
"""
from datetime import datetime
from pydantic import BaseModel

class NewsArticleOut(BaseModel):
    id: str
    headline: str
    source: str
    url: str
    published_at: datetime
    symbols: list | None
    impact_score: float | None
    sentiment_score: float | None
    created_at: datetime
    class Config: from_attributes = True

class NewsSentimentSummaryOut(BaseModel):
    symbol: str
    period_hours: int
    composite_score: float
    bullish_count: int
    bearish_count: int
    neutral_count: int
    article_count: int
    top_headlines: list[str]
