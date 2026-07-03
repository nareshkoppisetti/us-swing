"""
File path: backend/modules/market_data/models.py
Purpose: ORM models for symbol registry and commodity data.
         OHLCV time-series is stored in Parquet files (not SQLite).

SPEC Reference: Section 10.2, 11.1
"""

import uuid
from datetime import datetime, date
from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, Date, JSON
from sqlalchemy.dialects.sqlite import TEXT

from core.database import Base


class Symbol(Base):
    """Master symbol registry. Populated by seed_symbol_registry.py."""
    __tablename__ = "symbols"

    id          = Column(TEXT, primary_key=True, default=lambda: str(uuid.uuid4()))
    ticker      = Column(String(20), unique=True, nullable=False, index=True)
    name        = Column(String(255), nullable=False)
    symbol_type = Column(String(20), nullable=False)  # stock | etf | futures | index
    exchange    = Column(String(50), nullable=True)
    sector      = Column(String(100), nullable=True)
    is_active   = Column(Boolean, default=True)
    created_at  = Column(DateTime, default=datetime.utcnow)
    updated_at  = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Symbol {self.ticker}: {self.name}>"


class CommodityData(Base):
    """Commodity supplemental data (open interest, inventory, supply). Used by agents 35–42."""
    __tablename__ = "commodity_data"

    id                  = Column(TEXT, primary_key=True, default=lambda: str(uuid.uuid4()))
    symbol              = Column(String(20), nullable=False, index=True)
    data_date           = Column(Date, nullable=False, index=True)
    open_interest       = Column(Integer, nullable=True)
    inventory_level     = Column(Float, nullable=True)
    supply_change_pct   = Column(Float, nullable=True)
    source              = Column(String(50), nullable=False)   # EIA | Nasdaq_Data_Link | CBOE
    extra_data          = Column(JSON, nullable=True)
    created_at          = Column(DateTime, default=datetime.utcnow)
