from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional
from enum import Enum


class Signal(str, Enum):
    BULLISH = "Bullish"
    BEARISH = "Bearish"
    NEUTRAL = "Neutral"


@dataclass
class AgentOutput:
    agent_id: int                       # Sequential 1–42
    agent_name: str
    signal: Signal
    score: float                        # 0.0–100.0
    confidence: float                   # 0.0–100.0
    weight: float                       # 0.0–1.0 normalized impact weight
    reasoning: str
    bullish_factors: list = field(default_factory=list)
    bearish_factors: list = field(default_factory=list)
    supporting_data: dict = field(default_factory=dict)
    llm_ready_summary: dict = field(default_factory=dict)
    data_freshness: str = ""            # ISO 8601 timestamp of most recent data used
    execution_time_ms: int = 0
    error: Optional[str] = None         # None if successful, error message if degraded


class BaseAgent(ABC):
    agent_id: int
    agent_name: str
    category: str
    refresh_frequency: str              # "realtime"|"5min"|"hourly"|"daily"|"weekly"
    dependencies: list = []             # IDs of agents that must run before this one
    tier: int = 1                       # 1 (MVP) | 2 (Production) | 3 (Future)

    @abstractmethod
    def run(self, symbol: str, context: dict) -> AgentOutput:
        """Execute agent analysis for the given symbol.
        context contains AgentOutput objects of dependency agents keyed by agent_id."""
        pass

    def validate_output(self, output: AgentOutput) -> bool:
        assert 0.0 <= output.score <= 100.0, f"Score out of range: {output.score}"
        assert 0.0 <= output.confidence <= 100.0, f"Confidence out of range: {output.confidence}"
        assert output.signal in Signal.__members__.values(), f"Invalid signal: {output.signal}"
        return True
