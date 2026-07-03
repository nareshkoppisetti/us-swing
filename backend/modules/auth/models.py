"""
File path: backend/modules/auth/models.py
Purpose: User and UserSession ORM models.

SPEC Reference: Section 8.3 (RBAC), 10.2 (Auth Schema)
BUILD_PLAN Reference: Phase 1.9
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Enum as SAEnum, ForeignKey
from sqlalchemy.dialects.sqlite import TEXT
from sqlalchemy.orm import relationship

from core.database import Base


class User(Base):
    __tablename__ = "users"

    id               = Column(TEXT, primary_key=True, default=lambda: str(uuid.uuid4()))
    username         = Column(String(64), unique=True, nullable=False, index=True)
    email            = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password  = Column(String(255), nullable=False)
    role             = Column(
        SAEnum("admin", "user", name="user_role"),
        nullable=False,
        default="user",
    )
    is_active        = Column(Boolean, default=True, nullable=False)
    last_login       = Column(DateTime, nullable=True)
    created_at       = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at       = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    sessions = relationship(
        "UserSession",
        back_populates="user",
        cascade="all, delete-orphan",
        foreign_keys="[UserSession.user_id]",
    )

    def __repr__(self):
        return f"<User {self.username} ({self.role})>"


class UserSession(Base):
    __tablename__ = "user_sessions"

    id                  = Column(TEXT, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id             = Column(TEXT, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    refresh_token_hash  = Column(String(64), unique=True, nullable=False)
    ip_address          = Column(String(45), nullable=True)
    user_agent          = Column(String(255), nullable=True)
    expires_at          = Column(DateTime, nullable=False)
    created_at          = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="sessions", foreign_keys=[user_id])
