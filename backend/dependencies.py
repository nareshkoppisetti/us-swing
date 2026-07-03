"""
File path: backend/dependencies.py
Purpose: Shared FastAPI dependency injection functions used across all routers.

SPEC Reference: Section 8.3 (RBAC), 17.2 (JWT)
BUILD_PLAN Reference: Phase 1.8
"""

import logging
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from core.database import get_db
from core.security import decode_access_token
from core.exceptions import AuthenticationError, AuthorizationError
from modules.auth.models import User

logger = logging.getLogger("app")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


# ── Current User ──────────────────────────────────────────────────────────────

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Validate the Bearer JWT and return the authenticated User ORM object.

    Raises:
        AuthenticationError: if token is missing, invalid, expired, or user not found.
    """
    if not token:
        raise AuthenticationError("Authentication token is required.")

    try:
        payload = decode_access_token(token)
    except AuthenticationError:
        raise

    user_id = payload.get("sub")
    if not user_id:
        raise AuthenticationError("Token payload is invalid.")

    user = db.get(User, user_id)
    if not user:
        raise AuthenticationError("User account not found.")
    if not user.is_active:
        raise AuthenticationError("User account is deactivated.")

    return user


# ── Role Guards ───────────────────────────────────────────────────────────────

def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """
    Require the admin role.
    Raises AuthorizationError for normal ("user") accounts.
    """
    if current_user.role != "admin":
        raise AuthorizationError("Admin role is required.")
    return current_user


# ── Optional Auth (for public-ish endpoints) ──────────────────────────────────

def get_optional_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User | None:
    """
    Returns the authenticated user if a valid token is provided, else None.
    Use for endpoints that work both authenticated and unauthenticated.
    """
    if not token:
        return None
    try:
        return get_current_user(token=token, db=db)
    except AuthenticationError:
        return None
