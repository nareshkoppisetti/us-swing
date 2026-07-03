"""
File path: backend/modules/auth/router.py
Purpose: Auth endpoints. Mounted at /api/v1/auth in main.py.

SPEC Reference: Section 16.2 (Auth API)
BUILD_PLAN Reference: Phase 1.11
"""

import logging
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from core.database import get_db
from core.middleware import success_response
from dependencies import get_current_user
from modules.auth.schemas import (
    LoginRequest, TokenResponse, RefreshRequest,
    UserOut, UserCreateRequest, PasswordChangeRequest,
)
from modules.auth.service import AuthService
from modules.auth.models import User

logger = logging.getLogger("app")
router = APIRouter(tags=["Authentication"])


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, request: Request, db: Session = Depends(get_db)):
    """
    Authenticate with username + password.
    Returns JWT access token (15 min) and refresh token (7 days).
    Rate limited to 5 req/min per IP (enforced by RateLimitMiddleware).
    """
    ip = request.client.host if request.client else None
    ua = request.headers.get("user-agent")
    service = AuthService(db)
    return service.login(payload.username, payload.password, ip=ip, ua=ua)


@router.post("/logout")
def logout(payload: RefreshRequest, db: Session = Depends(get_db)):
    """Revoke a refresh token session."""
    AuthService(db).logout(payload.refresh_token)
    return success_response({"message": "Logged out successfully."})


@router.post("/refresh", response_model=TokenResponse)
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)):
    """Exchange a valid refresh token for a new access token."""
    return AuthService(db).refresh_token(payload.refresh_token)


@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    """Return the current authenticated user's profile."""
    return current_user


@router.post("/change-password")
def change_password(
    payload: PasswordChangeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Change the current user's password."""
    AuthService(db).change_password(
        current_user, payload.current_password, payload.new_password
    )
    return success_response({"message": "Password changed successfully."})
