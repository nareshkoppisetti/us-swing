"""
File path: backend/modules/agents/models.py
Purpose: ORM models for agent definitions, run history, and output storage.
         Tables: agent_definitions, agent_runs, agent_outputs

SPEC Reference: Section 10.2
BUILD_PLAN Reference: Phase 1.13

Note: AgentOutput here is the SQLAlchemy ORM model for DB persistence.
      The dataclass AgentOutput in base_agent.py is the in-memory runtime object.
      Import as: from modules.agents.models import AgentOutput as AgentOutputModel
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, JSON, Text
from sqlalchemy.dialects.sqlite import TEXT

from core.database import Base


class AgentDefinition(Base):
    """Static metadata for each of the 42 agents. Populated by seed_agent_definitions.py."""
    __tablename__ = "agent_definitions"

    id               = Column(Integer, primary_key=True)   # 1–42
    name             = Column(String(100), nullable=False)
    category         = Column(String(50), nullable=False)  # Direction | News & Macro | etc.
    tier             = Column(Integer, nullable=False)      # 1 | 2
    refresh_frequency = Column(String(20), nullable=False) # 15min | hourly | daily | per_run
    dependencies     = Column(JSON, default=list)          # list of agent IDs
    description      = Column(Text, nullable=True)
    is_active        = Column(Boolean, default=True)
    created_at       = Column(DateTime, default=datetime.utcnow)
    updated_at       = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AgentRun(Base):
    """Records each full pipeline run (42-agent execution) for a symbol."""
    __tablename__ = "agent_runs"

    id              = Column(TEXT, primary_key=True, default=lambda: str(uuid.uuid4()))
    symbol          = Column(String(20), nullable=False, index=True)
    run_started_at  = Column(DateTime, nullable=False, default=datetime.utcnow)
    run_completed_at = Column(DateTime, nullable=True)
    total_agents    = Column(Integer, default=42)
    successful_agents = Column(Integer, nullable=True)
    failed_agents   = Column(Integer, nullable=True)
    status          = Column(String(20), default="running")  # running | complete | failed
    triggered_by    = Column(String(50), nullable=True)      # scheduler | manual | api
    created_at      = Column(DateTime, default=datetime.utcnow)


class AgentOutput(Base):
    """
    Persisted output of a single agent execution for a symbol.
    ORM model — do NOT confuse with the AgentOutput dataclass in base_agent.py.
    """
    __tablename__ = "agent_outputs"

    id              = Column(TEXT, primary_key=True, default=lambda: str(uuid.uuid4()))
    agent_run_id    = Column(TEXT, nullable=False, index=True)
    agent_id        = Column(Integer, nullable=False, index=True)
    symbol          = Column(String(20), nullable=False, index=True)
    signal          = Column(String(10), nullable=False)    # Bullish | Bearish | Neutral
    score           = Column(Float, nullable=False)         # 0.0–100.0
    confidence      = Column(Float, nullable=False)         # 0.0–100.0
    weight          = Column(Float, nullable=False)         # 0.0–1.0
    reasoning       = Column(Text, nullable=True)
    bullish_factors = Column(JSON, default=list)
    bearish_factors = Column(JSON, default=list)
    supporting_data = Column(JSON, default=dict)
    llm_ready_summary = Column(JSON, default=dict)
    data_freshness  = Column(String(50), nullable=True)
    execution_time_ms = Column(Integer, nullable=True)
    error           = Column(Text, nullable=True)
    created_at      = Column(DateTime, default=datetime.utcnow, index=True)
