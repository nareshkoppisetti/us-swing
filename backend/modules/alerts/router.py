"""
File path: backend/modules/alerts/router.py
Endpoints (per API.md "Alerts", mounted at /api/v1/alerts):
  GET    /alerts        — list current user's alerts
  POST   /alerts        — create a new alert
  PATCH  /alerts/{id}   — update alert settings
  DELETE /alerts/{id}   — delete an alert
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from dependencies import get_db, get_current_user
from modules.alerts.schemas import AlertCreate
from modules.alerts.service import AlertService

router = APIRouter(tags=["Alerts"])


def _alert_out(a):
    return {
        "id": a.id, "user_id": a.user_id, "symbol": a.symbol, "alert_type": a.alert_type,
        "threshold_value": a.threshold_value, "direction_filter": a.direction_filter,
        "horizon_filter": a.horizon_filter, "is_active": a.is_active,
        "notify_email": a.notify_email, "notify_in_app": a.notify_in_app,
        "last_triggered_at": a.last_triggered_at, "trigger_count": a.trigger_count,
        "created_at": a.created_at,
    }


@router.get("/")
def list_alerts(db: Session = Depends(get_db), user=Depends(get_current_user)):
    svc = AlertService(db)
    alerts = svc.get_user_alerts(user.id)
    return {"success": True, "data": [_alert_out(a) for a in alerts], "meta": {"count": len(alerts)}}


@router.post("/")
def create_alert(req: AlertCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    svc = AlertService(db)
    alert = svc.create_alert(
        user_id=user.id, symbol=req.symbol, alert_type=req.alert_type,
        threshold_value=req.threshold_value, direction_filter=req.direction_filter,
        horizon_filter=req.horizon_filter, notify_email=req.notify_email, notify_in_app=req.notify_in_app,
    )
    return {"success": True, "data": _alert_out(alert), "meta": {}}


@router.patch("/{alert_id}")
def update_alert(alert_id: str, payload: dict, db: Session = Depends(get_db), user=Depends(get_current_user)):
    svc = AlertService(db)
    alert = svc.update_alert(alert_id, user.id, **payload)
    return {"success": True, "data": _alert_out(alert), "meta": {}}


@router.delete("/{alert_id}")
def delete_alert(alert_id: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    svc = AlertService(db)
    svc.delete_alert(alert_id, user.id)
    return {"success": True, "data": {"deleted": True}, "meta": {}}
