"""
File path: backend/modules/monitoring/router.py
Endpoints (per API.md "Monitoring (Admin)", mounted at /api/v1/monitoring):
  GET /monitoring/health        — full system health dashboard
  GET /monitoring/agents        — all 42 agent health statuses
  GET /monitoring/data-sources  — data source circuit breaker states
  GET /monitoring/api-keys      — external API request counts vs daily limits
  GET /monitoring/metrics       — latest system resource metrics (triggers a fresh snapshot)
All endpoints require the admin role.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from dependencies import get_db, require_admin
from modules.monitoring.service import MonitoringService

router = APIRouter(tags=["Monitoring"])


@router.get("/health")
def get_health_dashboard(db: Session = Depends(get_db), _=Depends(require_admin)):
    svc = MonitoringService(db)
    dashboard = svc.get_dashboard()
    return {"success": True, "data": dashboard, "meta": {}}


@router.get("/agents")
def get_agent_health(db: Session = Depends(get_db), _=Depends(require_admin)):
    svc = MonitoringService(db)
    dashboard = svc.get_dashboard()
    return {"success": True, "data": dashboard["agent_health"], "meta": {}}


@router.get("/data-sources")
def get_data_source_health(db: Session = Depends(get_db), _=Depends(require_admin)):
    svc = MonitoringService(db)
    dashboard = svc.get_dashboard()
    return {"success": True, "data": dashboard["data_sources"], "meta": {}}


@router.get("/api-keys")
def get_api_health(db: Session = Depends(get_db), _=Depends(require_admin)):
    svc = MonitoringService(db)
    results = svc.check_api_health()
    return {"success": True, "data": results, "meta": {}}


@router.get("/metrics")
def get_system_metrics(db: Session = Depends(get_db), _=Depends(require_admin)):
    svc = MonitoringService(db)
    metrics = svc.collect_system_metrics()
    return {"success": True, "data": metrics, "meta": {}}
