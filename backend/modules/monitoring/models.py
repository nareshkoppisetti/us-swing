"""
File path: backend/modules/monitoring/models.py
Purpose: SQLAlchemy models for system health monitoring.
         Tables: system_metrics, api_health, data_source_health, agent_health
         Per SPEC Section 10.2 and FR-006.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, JSON
from sqlalchemy.dialects.sqlite import TEXT
try:
    from core.database import Base
except ImportError:
    from sqlalchemy.orm import declarative_base; Base = declarative_base()

class SystemMetrics(Base):
    """Periodic system resource snapshots."""
    __tablename__ = "system_metrics"
    id = Column(TEXT, primary_key=True, default=lambda: str(uuid.uuid4()))
    recorded_at = Column(DateTime, nullable=False, index=True)
    cpu_pct = Column(Float, nullable=True)
    memory_pct = Column(Float, nullable=True)
    disk_usage_pct = Column(Float, nullable=True)
    active_db_connections = Column(Integer, nullable=True)
    api_request_count_1h = Column(Integer, nullable=True)
    api_error_rate_1h = Column(Float, nullable=True)
    avg_response_ms_1h = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class APIHealth(Base):
    """Tracks health status of each external API dependency."""
    __tablename__ = "api_health"
    id = Column(TEXT, primary_key=True, default=lambda: str(uuid.uuid4()))
    api_name = Column(String(100), nullable=False, index=True)
    checked_at = Column(DateTime, nullable=False)
    status = Column(String(20), nullable=False)  # healthy | degraded | down
    response_ms = Column(Integer, nullable=True)
    error_message = Column(String(500), nullable=True)
    requests_today = Column(Integer, nullable=True)
    daily_limit = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class DataSourceHealth(Base):
    """Circuit breaker state and freshness per data source."""
    __tablename__ = "data_source_health"
    id = Column(TEXT, primary_key=True, default=lambda: str(uuid.uuid4()))
    source_name = Column(String(100), nullable=False, unique=True, index=True)
    status = Column(String(20), nullable=False)      # healthy | degraded | circuit_open
    failure_count = Column(Integer, default=0)
    circuit_open_until = Column(DateTime, nullable=True)
    last_success_at = Column(DateTime, nullable=True)
    last_failure_at = Column(DateTime, nullable=True)
    data_freshness_mins = Column(Integer, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class AgentHealth(Base):
    """Per-agent health tracking: last run, duration, error count."""
    __tablename__ = "agent_health"
    id = Column(TEXT, primary_key=True, default=lambda: str(uuid.uuid4()))
    agent_id = Column(Integer, nullable=False, unique=True, index=True)
    agent_name = Column(String(100), nullable=False)
    status = Column(String(20), nullable=False)      # healthy | warning | failed
    last_run_at = Column(DateTime, nullable=True)
    last_run_duration_ms = Column(Integer, nullable=True)
    error_count_24h = Column(Integer, default=0)
    accuracy_30d = Column(Float, nullable=True)
    data_freshness = Column(String(50), nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AuditLog(Base):
    """
    Audit trail for all write operations performed by users.
    Added to match BUILD_PLAN Phase 11.8 requirement.
    Track: who changed what, when, and what the old/new values were.
    """
    __tablename__ = "audit_logs"

    id = Column(TEXT, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(TEXT, nullable=True, index=True)       # nullable for system actions
    action = Column(String(50), nullable=False, index=True) # create | update | delete | trigger
    resource_type = Column(String(50), nullable=False)      # prediction | user | agent | signal | alert
    resource_id = Column(TEXT, nullable=True)
    old_value = Column(JSON, nullable=True)
    new_value = Column(JSON, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(255), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
