"""
File path: backend/modules/admin/schemas.py
Purpose: Pydantic schemas for admin user management, scheduler, and settings.
Per API.md "Admin" section.
"""
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, EmailStr, field_validator


class UserOut(BaseModel):
    id: str
    username: str
    email: str
    role: str
    is_active: bool
    last_login: Optional[datetime] = None
    created_at: datetime
    class Config: from_attributes = True


class AdminCreateUserRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: str = "user"

    @field_validator("role")
    @classmethod
    def valid_role(cls, v: str) -> str:
        allowed = {"admin", "user"}
        if v not in allowed:
            raise ValueError(f"Role must be one of: {allowed}")
        return v

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters.")
        return v


class AdminUpdateUserRequest(BaseModel):
    role: Optional[str] = None
    is_active: Optional[bool] = None

    @field_validator("role")
    @classmethod
    def valid_role(cls, v):
        if v is not None and v not in {"admin", "user"}:
            raise ValueError("Role must be one of: {'admin', 'user'}")
        return v


class SchedulerJobOut(BaseModel):
    id: str
    name: str
    next_run: Optional[str] = None


class SettingOut(BaseModel):
    key: str
    value: Any
    updated_at: Optional[datetime] = None
