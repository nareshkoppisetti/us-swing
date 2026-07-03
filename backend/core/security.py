"""
File path: backend/core/security.py
Purpose: JWT creation/validation and password hashing utilities.
         Used by auth/service.py and dependencies.py.

SPEC Reference: Section 17.2 (JWT Implementation)
BUILD_PLAN Reference: Phase 1.4

JWT payload structure:
  {
    "sub":  "user-uuid",          # user ID
    "role": "user",               # user role (for RBAC checks)
    "type": "access"|"refresh",   # token type
    "exp":  1234567890            # expiry timestamp
  }
"""

import hashlib
import logging
import secrets
from datetime import datetime, timedelta, timezone
from typing import Literal

from jose import JWTError, jwt
from passlib.context import CryptContext

from config import settings
from core.exceptions import AuthenticationError

logger = logging.getLogger("app")

# ── Password hashing ──────────────────────────────────────────────────────────

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a plain-text password with bcrypt. Returns the hashed string."""
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    """Verify a plain-text password against a bcrypt hash."""
    return pwd_context.verify(plain, hashed)


# ── JWT ───────────────────────────────────────────────────────────────────────

def _now() -> datetime:
    return datetime.now(timezone.utc)


def create_access_token(user_id: str, role: str) -> str:
    """
    Create a short-lived JWT access token (15 min TTL per SPEC 17.2).

    Args:
        user_id: UUID string of the user
        role:    User role string (admin | user)

    Returns:
        Signed JWT string
    """
    expire = _now() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub":  user_id,
        "role": role,
        "type": "access",
        "exp":  expire,
        "iat":  _now(),
    }
    return jwt.encode(payload, settings.APP_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(user_id: str) -> tuple[str, str]:
    """
    Create a long-lived refresh token (7 day TTL per SPEC 17.2).

    Returns:
        (raw_token: str, token_hash: str)
        — raw_token is returned to client once (never stored)
        — token_hash is stored in user_sessions table for validation

    Refresh tokens are opaque random strings (not JWT) to prevent
    information leakage on expiry. Hash stored with SHA-256.
    """
    raw_token = secrets.token_urlsafe(48)
    token_hash = _hash_refresh_token(raw_token)
    return raw_token, token_hash


def _hash_refresh_token(raw_token: str) -> str:
    """SHA-256 hash of a raw refresh token for safe DB storage."""
    return hashlib.sha256(raw_token.encode()).hexdigest()


def decode_access_token(token: str) -> dict:
    """
    Decode and validate a JWT access token.

    Returns:
        Payload dict with 'sub' (user_id) and 'role' keys.

    Raises:
        AuthenticationError: if token is expired, tampered, or wrong type.
    """
    try:
        payload = jwt.decode(
            token,
            settings.APP_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
    except JWTError as e:
        raise AuthenticationError(f"Invalid or expired token: {e}")

    if payload.get("type") != "access":
        raise AuthenticationError("Token type mismatch — expected access token.")

    return payload


def decode_refresh_token_hash(raw_token: str) -> str:
    """
    Convert a raw refresh token back to its stored hash for DB lookup.
    Called by AuthService.refresh_token().
    """
    return _hash_refresh_token(raw_token)
