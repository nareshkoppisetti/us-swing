"""
File path: backend/modules/admin/models.py
Purpose: SQLAlchemy model for platform settings (confidence_threshold,
         watch_symbols, api_rate_limits, etc.) editable via GET/PATCH
         /admin/settings. Simple key-value store — values are JSON-encoded.
Per SPEC Section 8.3 / API.md "Admin".
"""
import uuid
from datetime import datetime

from sqlalchemy import Column, String, JSON, DateTime
from sqlalchemy.dialects.sqlite import TEXT

from core.database import Base


class SystemSetting(Base):
    """Generic key-value platform settings store."""
    __tablename__ = "system_settings"

    key = Column(String(100), primary_key=True)
    value = Column(JSON, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = Column(TEXT, nullable=True)  # user_id of last editor
