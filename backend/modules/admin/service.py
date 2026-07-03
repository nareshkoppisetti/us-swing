"""
File path: backend/modules/admin/service.py
Purpose: AdminService — business logic for user management, scheduler
         control, and platform settings.
Per SPEC Section 8.3 (RBAC) and API.md "Admin".
"""
import logging
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from core.exceptions import NotFoundError, ValidationError
from modules.admin.models import SystemSetting
from modules.auth.models import User
from modules.auth.service import AuthService

logger = logging.getLogger("app")

# Default platform settings — seeded on first read if the row doesn't exist yet.
DEFAULT_SETTINGS = {
    "confidence_threshold": 60.0,
    "watch_symbols": ["SPY", "QQQ", "AAPL", "TSLA", "NVDA", "MSFT", "AMZN", "GOOGL"],
    "api_rate_limits": {
        "alpha_vantage_per_day": 25,
        "newsapi_per_day": 100,
    },
}


class AdminService:
    def __init__(self, db: Session, scheduler=None):
        self.db = db
        self.scheduler = scheduler

    # ── Users ────────────────────────────────────────────────────────────────
    def list_users(self) -> list:
        return self.db.query(User).order_by(User.created_at).all()

    def create_user(self, username: str, email: str, password: str, role: str) -> User:
        auth = AuthService(self.db)
        return auth.create_user(username=username, email=email, password=password, role=role)

    def update_user(self, user_id: str, role: Optional[str] = None, is_active: Optional[bool] = None) -> User:
        user = self.db.query(User).filter(User.id == user_id).first()
        if user is None:
            raise NotFoundError(f"User '{user_id}' not found")
        if role is not None:
            user.role = role
        if is_active is not None:
            user.is_active = is_active
        user.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(user)
        return user

    def deactivate_user(self, user_id: str) -> None:
        user = self.db.query(User).filter(User.id == user_id).first()
        if user is None:
            raise NotFoundError(f"User '{user_id}' not found")
        user.is_active = False
        user.updated_at = datetime.utcnow()
        self.db.commit()

    # ── Settings ─────────────────────────────────────────────────────────────
    def get_settings(self) -> dict:
        """Read all platform settings, seeding defaults for any missing key."""
        rows = {r.key: r.value for r in self.db.query(SystemSetting).all()}
        result = {}
        changed = False
        for key, default in DEFAULT_SETTINGS.items():
            if key in rows:
                result[key] = rows[key]
            else:
                result[key] = default
                self.db.add(SystemSetting(key=key, value=default))
                changed = True
        if changed:
            self.db.commit()
        return result

    def update_settings(self, payload: dict, updated_by: str = None) -> dict:
        """Persist updated platform settings (partial update allowed)."""
        for key, value in payload.items():
            if key not in DEFAULT_SETTINGS:
                raise ValidationError(f"Unknown setting key: '{key}'")
            row = self.db.query(SystemSetting).filter(SystemSetting.key == key).first()
            if row is None:
                row = SystemSetting(key=key, value=value, updated_by=updated_by)
                self.db.add(row)
            else:
                row.value = value
                row.updated_at = datetime.utcnow()
                row.updated_by = updated_by
        self.db.commit()
        return self.get_settings()

    # ── Scheduler ────────────────────────────────────────────────────────────
    def list_scheduler_jobs(self) -> list:
        from modules.agents.scheduler import get_scheduler_status
        status = get_scheduler_status()
        return status["jobs"]

    def trigger_job(self, job_id: str) -> dict:
        from modules.agents.scheduler import trigger_job as scheduler_trigger_job
        return scheduler_trigger_job(job_id)
