"""
File path: backend/modules/monitoring/schemas.py
Purpose: Pydantic schemas for monitoring/health API responses.
"""
from datetime import datetime
from pydantic import BaseModel


class SystemMetricsOut(BaseModel):
    recorded_at: datetime
    cpu_pct: float | None
    memory_pct: float | None
    disk_usage_pct: float | None
    active_db_connections: int | None
    api_request_count_1h: int | None
    api_error_rate_1h: float | None
    avg_response_ms_1h: float | None
    class Config: from_attributes = True


class APIHealthOut(BaseModel):
    api_name: str
    checked_at: datetime
    status: str          # healthy | degraded | down
    response_ms: int | None
    error_message: str | None
    requests_today: int | None
    daily_limit: int | None
    class Config: from_attributes = True


class DataSourceHealthOut(BaseModel):
    source_name: str
    status: str          # healthy | degraded | circuit_open
    failure_count: int
    circuit_open_until: datetime | None
    last_success_at: datetime | None
    last_failure_at: datetime | None
    data_freshness_mins: int | None
    class Config: from_attributes = True


class AgentHealthOut(BaseModel):
    agent_id: int
    agent_name: str
    status: str          # healthy | warning | failed
    last_run_at: datetime | None
    last_run_duration_ms: int | None
    error_count_24h: int
    accuracy_30d: float | None
    data_freshness: str | None
    class Config: from_attributes = True


class SystemHealthDashboardOut(BaseModel):
    """Full health dashboard returned by GET /monitoring/health."""
    overall_status: str  # healthy | degraded | critical
    system_metrics: SystemMetricsOut | None
    api_health: list[APIHealthOut]
    data_sources: list[DataSourceHealthOut]
    agent_health: list[AgentHealthOut]
    generated_at: datetime
