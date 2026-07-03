"""
File path: backend/modules/symbol_search/schemas.py
Purpose: Pydantic schemas for symbol search API responses.
"""
from datetime import datetime
from pydantic import BaseModel


class SymbolOut(BaseModel):
    id: str
    ticker: str
    name: str
    symbol_type: str    # stock | etf | futures | index
    exchange: str | None
    sector: str | None
    is_active: bool
    class Config: from_attributes = True


class SymbolSearchResult(BaseModel):
    """Lightweight result for autocomplete dropdown."""
    ticker: str
    name: str
    symbol_type: str
    exchange: str | None
    sector: str | None


class SymbolSearchResponse(BaseModel):
    query: str
    results: list[SymbolSearchResult]
    total: int
