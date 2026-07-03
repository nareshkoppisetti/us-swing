"""
File path: backend/modules/agents/schemas.py
Purpose: Pydantic schemas for agent API responses.
"""

from datetime import datetime
from pydantic import BaseModel


class AgentDefinitionOut(BaseModel):
    """Agent static definition metadata."""
    agent_id: int
    agent_name: str
    category: str
    tier: int
    refresh_frequency: str
    dependencies: list[int]
    description: str


class AgentOutputOut(BaseModel):
    """API-serializable version of AgentOutput dataclass."""
    agent_id: int
    agent_name: str
    signal: str  # Bullish | Bearish | Neutral
    score: float
    confidence: float
    weight: float
    reasoning: str
    bullish_factors: list[str]
    bearish_factors: list[str]
    supporting_data: dict
    llm_ready_summary: dict
    data_freshness: str
    execution_time_ms: int
    error: str | None
    created_at: datetime | None


class AgentHealthOut(BaseModel):
    """Agent health/monitoring status for admin panel."""
    agent_id: int
    agent_name: str
    status: str  # healthy | warning | failed
    last_run_at: datetime | None
    last_run_duration_ms: int | None
    error_count_24h: int
    accuracy_30d: float | None
    data_freshness: str | None
