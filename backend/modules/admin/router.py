"""
File path: backend/modules/admin/router.py
Endpoints (per API.md "Admin", mounted at /api/v1/admin):
  GET/POST   /admin/users
  PATCH/DELETE /admin/users/{id}
  GET        /admin/scheduler/jobs
  POST       /admin/scheduler/{job_id}/trigger
  GET/PATCH  /admin/settings
All endpoints require the admin role.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from dependencies import get_db, require_admin
from modules.admin.schemas import AdminCreateUserRequest, AdminUpdateUserRequest
from modules.admin.service import AdminService

router = APIRouter(tags=["Admin"])


def _user_out(u):
    return {
        "id": u.id, "username": u.username, "email": u.email, "role": u.role,
        "is_active": u.is_active, "last_login": u.last_login, "created_at": u.created_at,
    }


@router.get("/users")
def list_users(db: Session = Depends(get_db), _=Depends(require_admin)):
    svc = AdminService(db)
    users = svc.list_users()
    return {"success": True, "data": [_user_out(u) for u in users], "meta": {"count": len(users)}}


@router.post("/users")
def create_user(req: AdminCreateUserRequest, db: Session = Depends(get_db), _=Depends(require_admin)):
    svc = AdminService(db)
    user = svc.create_user(username=req.username, email=req.email, password=req.password, role=req.role)
    return {"success": True, "data": _user_out(user), "meta": {}}


@router.patch("/users/{user_id}")
def update_user(user_id: str, req: AdminUpdateUserRequest, db: Session = Depends(get_db), _=Depends(require_admin)):
    svc = AdminService(db)
    user = svc.update_user(user_id, role=req.role, is_active=req.is_active)
    return {"success": True, "data": _user_out(user), "meta": {}}


@router.delete("/users/{user_id}")
def deactivate_user(user_id: str, db: Session = Depends(get_db), _=Depends(require_admin)):
    svc = AdminService(db)
    svc.deactivate_user(user_id)
    return {"success": True, "data": {"deactivated": True}, "meta": {}}


@router.get("/scheduler/jobs")
def list_scheduler_jobs(db: Session = Depends(get_db), _=Depends(require_admin)):
    svc = AdminService(db)
    jobs = svc.list_scheduler_jobs()
    return {"success": True, "data": jobs, "meta": {"count": len(jobs)}}


@router.post("/scheduler/{job_id}/trigger")
def trigger_scheduler_job(job_id: str, db: Session = Depends(get_db), _=Depends(require_admin)):
    svc = AdminService(db)
    result = svc.trigger_job(job_id)
    return {"success": True, "data": result, "meta": {}}


@router.get("/logs")
def get_audit_logs(
    page: int = 1, per_page: int = 50, resource_type: str = None,
    db: Session = Depends(get_db), _=Depends(require_admin),
):
    from modules.monitoring.models import AuditLog
    q = db.query(AuditLog).order_by(AuditLog.timestamp.desc())
    if resource_type:
        q = q.filter(AuditLog.resource_type == resource_type)
    total = q.count()
    rows = q.offset((page - 1) * per_page).limit(per_page).all()
    data = [{
        "id": r.id, "user_id": r.user_id, "action": r.action,
        "resource_type": r.resource_type, "resource_id": r.resource_id,
        "old_value": r.old_value, "new_value": r.new_value,
        "ip_address": r.ip_address, "timestamp": r.timestamp,
    } for r in rows]
    return {"success": True, "data": data, "meta": {"page": page, "per_page": per_page, "total": total}}


@router.get("/settings")
def get_settings(db: Session = Depends(get_db), _=Depends(require_admin)):
    svc = AdminService(db)
    return {"success": True, "data": svc.get_settings(), "meta": {}}


@router.patch("/settings")
def update_settings(payload: dict, db: Session = Depends(get_db), admin=Depends(require_admin)):
    svc = AdminService(db)
    updated = svc.update_settings(payload, updated_by=admin.id)
    return {"success": True, "data": updated, "meta": {}}
