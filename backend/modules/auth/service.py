"""
File path: backend/modules/auth/service.py
Purpose: AuthService — all authentication business logic.

SPEC Reference: Section 8.3, 17.2
BUILD_PLAN Reference: Phase 1.10
"""

import logging
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session

from config import settings
from core.exceptions import AuthenticationError, NotFoundError, ConflictError
from core.security import (
    hash_password, verify_password,
    create_access_token, create_refresh_token, decode_refresh_token_hash,
)
from modules.auth.models import User, UserSession
from modules.auth.schemas import TokenResponse, UserOut

logger = logging.getLogger("app")


class AuthService:
    def __init__(self, db: Session):
        self.db = db

    # ── Login ─────────────────────────────────────────────────────────────────

    def login(self, username: str, password: str, ip: str | None = None, ua: str | None = None) -> TokenResponse:
        """
        Authenticate with username + password.
        Returns TokenResponse with access + refresh tokens.
        Raises AuthenticationError on bad credentials or inactive account.
        """
        user = self.db.query(User).filter(User.username == username).first()

        if not user or not verify_password(password, user.hashed_password):
            logger.warning("login_failed", extra={"username": username, "ip": ip})
            raise AuthenticationError("Invalid username or password.")

        if not user.is_active:
            raise AuthenticationError("Account is deactivated. Contact an administrator.")

        # Create tokens
        access_token = create_access_token(user.id, user.role)
        raw_refresh, refresh_hash = create_refresh_token(user.id)

        # Store refresh token session
        expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        session = UserSession(
            user_id=user.id,
            refresh_token_hash=refresh_hash,
            ip_address=ip,
            user_agent=ua,
            expires_at=expires_at,
        )
        self.db.add(session)

        # Update last_login
        user.last_login = datetime.utcnow()
        self.db.flush()

        logger.info("login_success", extra={"user_id": user.id, "role": user.role})

        return TokenResponse(
            access_token=access_token,
            refresh_token=raw_refresh,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=UserOut.model_validate(user),
        )

    # ── Refresh ───────────────────────────────────────────────────────────────

    def refresh_token(self, raw_refresh_token: str) -> TokenResponse:
        """
        Exchange a valid refresh token for a new access token.
        Raises AuthenticationError if token is invalid or expired.
        """
        token_hash = decode_refresh_token_hash(raw_refresh_token)
        session = (
            self.db.query(UserSession)
            .filter(UserSession.refresh_token_hash == token_hash)
            .first()
        )

        if not session:
            raise AuthenticationError("Refresh token is invalid or has been revoked.")

        if datetime.now(timezone.utc) > session.expires_at.replace(tzinfo=timezone.utc):
            self.db.delete(session)
            raise AuthenticationError("Refresh token has expired. Please log in again.")

        user = self.db.get(User, session.user_id)
        if not user or not user.is_active:
            raise AuthenticationError("User account not found or deactivated.")

        new_access_token = create_access_token(user.id, user.role)

        return TokenResponse(
            access_token=new_access_token,
            refresh_token=raw_refresh_token,   # same refresh token
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=UserOut.model_validate(user),
        )

    # ── Logout ────────────────────────────────────────────────────────────────

    def logout(self, raw_refresh_token: str) -> None:
        """Revoke the refresh token session. Silent if already revoked."""
        token_hash = decode_refresh_token_hash(raw_refresh_token)
        session = (
            self.db.query(UserSession)
            .filter(UserSession.refresh_token_hash == token_hash)
            .first()
        )
        if session:
            self.db.delete(session)

    # ── User management ───────────────────────────────────────────────────────

    def create_user(self, username: str, email: str, password: str, role: str = "user") -> User:
        """Create a new user. Raises ConflictError if username/email already exists."""
        if self.db.query(User).filter(User.username == username).first():
            raise ConflictError(f"Username '{username}' is already taken.")
        if self.db.query(User).filter(User.email == email).first():
            raise ConflictError(f"Email '{email}' is already registered.")

        user = User(
            username=username,
            email=email,
            hashed_password=hash_password(password),
            role=role,
        )
        self.db.add(user)
        self.db.flush()
        logger.info("user_created", extra={"user_id": user.id, "role": role})
        return user

    def get_user_by_id(self, user_id: str) -> User:
        user = self.db.get(User, user_id)
        if not user:
            raise NotFoundError(f"User {user_id} not found.")
        return user

    def change_password(self, user: User, current_password: str, new_password: str) -> None:
        """Change a user's password after verifying the current one."""
        if not verify_password(current_password, user.hashed_password):
            raise AuthenticationError("Current password is incorrect.")
        user.hashed_password = hash_password(new_password)
        self.db.flush()
