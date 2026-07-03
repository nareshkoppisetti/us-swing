"""
File path: backend/modules/performance/router.py
Endpoints (per API.md "Performance", mounted at /api/v1/performance):
  GET  /performance/accuracy?symbol=&horizon=&days=
  GET  /performance/calibration
  GET  /performance/history?symbol=&limit=
  POST /performance/resolve   — admin only
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from dependencies import get_db, get_current_user, require_admin
from modules.performance.service import PerformanceService

router = APIRouter(tags=["Performance"])


def _history_out(r):
    return {
        "id": r.id, "symbol": r.symbol, "horizon_days": r.horizon_days,
        "predicted_direction": r.predicted_direction, "actual_direction": r.actual_direction,
        "is_correct": r.is_correct, "predicted_confidence": r.predicted_confidence,
        "actual_move_pct": r.actual_move_pct, "resolved_at": r.resolved_at,
    }


@router.get("/accuracy")
def get_accuracy(symbol: str = Query(None), horizon: int = Query(None), days: int = Query(30),
                  db: Session = Depends(get_db), _=Depends(get_current_user)):
    svc = PerformanceService(db)
    data = svc.get_accuracy_summary(symbol=symbol, horizon=horizon, days=days)
    return {"success": True, "data": data, "meta": {}}


@router.get("/calibration")
def get_calibration(db: Session = Depends(get_db), _=Depends(get_current_user)):
    svc = PerformanceService(db)
    data = svc.get_calibration_report()
    return {"success": True, "data": data, "meta": {}}


@router.get("/history")
def get_history(symbol: str = Query(None), limit: int = Query(50), db: Session = Depends(get_db), _=Depends(get_current_user)):
    svc = PerformanceService(db)
    rows = svc.get_resolved_history(symbol=symbol, limit=limit)
    return {"success": True, "data": [_history_out(r) for r in rows], "meta": {"count": len(rows)}}


@router.post("/resolve")
def resolve_predictions(db: Session = Depends(get_db), _=Depends(require_admin)):
    svc = PerformanceService(db)
    count = svc.resolve_expired_predictions()
    return {"success": True, "data": {"resolved_count": count}, "meta": {}}
