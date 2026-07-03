"""
File path: backend/modules/monitoring/service.py
Purpose: MonitoringService — collects and exposes system health metrics.
Per SPEC Section 10.2 / FR-006 and API.md "Monitoring (Admin)".
"""
import logging
import time
from datetime import datetime, timedelta

import psutil
import requests
from sqlalchemy.orm import Session

from config import settings
from modules.monitoring.models import SystemMetrics, APIHealth, DataSourceHealth, AgentHealth

logger = logging.getLogger("app")

# External APIs we can meaningfully health-check with a lightweight call.
# (name, check_fn) — check_fn returns (ok: bool, response_ms: int, error: str|None)
def _check_alpha_vantage():
    start = time.time()
    try:
        r = requests.get(
            "https://www.alphavantage.co/query",
            params={"function": "GLOBAL_QUOTE", "symbol": "AAPL", "apikey": settings.ALPHA_VANTAGE_API_KEY},
            timeout=5,
        )
        ms = int((time.time() - start) * 1000)
        ok = r.status_code == 200 and "Note" not in r.text and "Error Message" not in r.text
        return ok, ms, None if ok else "rate-limited or invalid key"
    except Exception as e:
        return False, int((time.time() - start) * 1000), str(e)


def _check_fred():
    start = time.time()
    try:
        r = requests.get(
            "https://api.stlouisfed.org/fred/series",
            params={"series_id": "GDP", "api_key": settings.FRED_API_KEY, "file_type": "json"},
            timeout=5,
        )
        ms = int((time.time() - start) * 1000)
        return r.status_code == 200, ms, None if r.status_code == 200 else f"HTTP {r.status_code}"
    except Exception as e:
        return False, int((time.time() - start) * 1000), str(e)


def _check_newsapi():
    start = time.time()
    try:
        r = requests.get(
            "https://newsapi.org/v2/top-headlines",
            params={"category": "business", "pageSize": 1, "apiKey": settings.NEWS_API_KEY},
            timeout=5,
        )
        ms = int((time.time() - start) * 1000)
        return r.status_code == 200, ms, None if r.status_code == 200 else f"HTTP {r.status_code}"
    except Exception as e:
        return False, int((time.time() - start) * 1000), str(e)


def _check_eia():
    start = time.time()
    try:
        r = requests.get(
            "https://api.eia.gov/v2/petroleum/pri/spt/data/",
            params={"api_key": settings.EIA_API_KEY, "frequency": "daily", "data[0]": "value", "length": 1},
            timeout=5,
        )
        ms = int((time.time() - start) * 1000)
        return r.status_code == 200, ms, None if r.status_code == 200 else f"HTTP {r.status_code}"
    except Exception as e:
        return False, int((time.time() - start) * 1000), str(e)


API_CHECKS = {
    "alpha_vantage": (_check_alpha_vantage, 25),   # free-tier daily limit
    "fred": (_check_fred, None),
    "newsapi": (_check_newsapi, 100),
    "eia": (_check_eia, None),
}


class MonitoringService:
    def __init__(self, db: Session):
        self.db = db

    # ── System resources ────────────────────────────────────────────────────
    def collect_system_metrics(self) -> dict:
        """Snapshot CPU/memory/disk via psutil and persist a SystemMetrics row."""
        cpu_pct = psutil.cpu_percent(interval=0.2)
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage("/")

        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        # Best-effort request-rate stats — audit_logs isn't guaranteed to have
        # every request, so this is a coarse approximation, not exact APM data.
        req_count = None
        try:
            from modules.monitoring.models import AuditLog
            req_count = (
                self.db.query(AuditLog)
                .filter(AuditLog.timestamp >= one_hour_ago)
                .count()
            )
        except Exception:
            pass

        row = SystemMetrics(
            recorded_at=datetime.utcnow(),
            cpu_pct=cpu_pct,
            memory_pct=mem.percent,
            disk_usage_pct=disk.percent,
            active_db_connections=None,  # SQLite has no connection pool concept
            api_request_count_1h=req_count,
            api_error_rate_1h=None,
            avg_response_ms_1h=None,
        )
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return {
            "recorded_at": row.recorded_at,
            "cpu_pct": row.cpu_pct,
            "memory_pct": row.memory_pct,
            "disk_usage_pct": row.disk_usage_pct,
            "active_db_connections": row.active_db_connections,
            "api_request_count_1h": row.api_request_count_1h,
            "api_error_rate_1h": row.api_error_rate_1h,
            "avg_response_ms_1h": row.avg_response_ms_1h,
        }

    # ── External API health ─────────────────────────────────────────────────
    def check_api_health(self) -> list:
        """Ping each external API with a cheap real request and record status."""
        results = []
        for name, (check_fn, daily_limit) in API_CHECKS.items():
            ok, ms, err = check_fn()
            status = "healthy" if ok else "down"
            row = APIHealth(
                api_name=name,
                checked_at=datetime.utcnow(),
                status=status,
                response_ms=ms,
                error_message=err,
                requests_today=None,
                daily_limit=daily_limit,
            )
            self.db.add(row)
            results.append({
                "api_name": name, "checked_at": row.checked_at, "status": status,
                "response_ms": ms, "error_message": err,
                "requests_today": None, "daily_limit": daily_limit,
            })
        self.db.commit()
        return results

    # ── Dashboard ────────────────────────────────────────────────────────────
    def get_dashboard(self) -> dict:
        """Full health dashboard: latest system metrics + API health + data sources + agents."""
        latest_metrics = (
            self.db.query(SystemMetrics).order_by(SystemMetrics.recorded_at.desc()).first()
        )
        if latest_metrics is None:
            self.collect_system_metrics()
            latest_metrics = (
                self.db.query(SystemMetrics).order_by(SystemMetrics.recorded_at.desc()).first()
            )

        # Latest API health row per api_name
        api_rows = self.db.query(APIHealth).order_by(APIHealth.checked_at.desc()).limit(50).all()
        seen, api_health = set(), []
        for r in api_rows:
            if r.api_name in seen:
                continue
            seen.add(r.api_name)
            api_health.append(r)

        data_sources = self.db.query(DataSourceHealth).all()
        agent_health = self.db.query(AgentHealth).order_by(AgentHealth.agent_id).all()

        overall = "healthy"
        if any(a.status == "down" for a in api_health) or any(d.status == "circuit_open" for d in data_sources):
            overall = "degraded"
        if any(a.status == "failed" for a in agent_health):
            overall = "critical"

        return {
            "overall_status": overall,
            "system_metrics": latest_metrics,
            "api_health": api_health,
            "data_sources": data_sources,
            "agent_health": agent_health,
            "generated_at": datetime.utcnow(),
        }

    # ── Called by AgentEngine / CollectorBase ───────────────────────────────
    def update_agent_health(self, agent_id: int, agent_name: str, duration_ms: int, error: str = None) -> None:
        """Upsert AgentHealth after each agent run."""
        row = self.db.query(AgentHealth).filter(AgentHealth.agent_id == agent_id).first()
        if row is None:
            row = AgentHealth(agent_id=agent_id, agent_name=agent_name, status="healthy", error_count_24h=0)
            self.db.add(row)

        row.agent_name = agent_name
        row.last_run_at = datetime.utcnow()
        row.last_run_duration_ms = duration_ms
        if error:
            row.status = "failed"
            row.error_count_24h = (row.error_count_24h or 0) + 1
        else:
            row.status = "healthy"
        self.db.commit()

    def update_data_source_health(self, source_name: str, status: str, failure_count: int = 0) -> None:
        """Upsert DataSourceHealth on circuit breaker state change."""
        row = self.db.query(DataSourceHealth).filter(DataSourceHealth.source_name == source_name).first()
        if row is None:
            row = DataSourceHealth(source_name=source_name, status=status, failure_count=failure_count)
            self.db.add(row)
        else:
            row.status = status
            row.failure_count = failure_count
        now = datetime.utcnow()
        if status == "healthy":
            row.last_success_at = now
        else:
            row.last_failure_at = now
            if status == "circuit_open":
                row.circuit_open_until = now + timedelta(minutes=10)
        row.updated_at = now
        self.db.commit()
