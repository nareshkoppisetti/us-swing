# USA Swing — Agent Developer Guide

**File path:** `docs/AGENT_GUIDE.md`  
**Purpose:** Step-by-step guide for implementing individual agents. Reference for all 42 agent implementations.

---

## Overview

USA Swing uses a 42-agent architecture where each agent is a focused analytical unit. Agents produce a standardized `AgentOutput` consumed by the aggregation layer (Agents 30–33).

**Full spec:** See `docs/SPEC.md` Section 12 (Agent Architecture).

---

## Agent Base Class

Every agent inherits from `BaseAgent` in `backend/modules/agents/base_agent.py`:

```python
class MyAgent(BaseAgent):
    agent_id = 1           # unique integer 1–42
    agent_name = "My Agent"
    category = "Direction"
    refresh_frequency = "15min"
    dependencies = []       # list of agent_ids this agent depends on
    tier = 1               # execution tier (1=parallel first pass, 2=after tier 1)

    def run(self, symbol: str, context: dict) -> AgentOutput:
        # context = {agent_id: AgentOutput} for dependency agents
        ...
```

---

## AgentOutput Schema

```python
@dataclass
class AgentOutput:
    agent_id: int
    agent_name: str
    signal: Signal             # Signal.BULLISH | BEARISH | NEUTRAL
    score: float               # 0.0–100.0 (50 = neutral)
    confidence: float          # 0.0–100.0
    weight: float              # 0.0–1.0 (impact weight)
    reasoning: str             # 1–3 sentence human-readable explanation
    bullish_factors: list[str] # data-backed bullish points
    bearish_factors: list[str] # data-backed bearish points
    supporting_data: dict      # raw data for auditability
    llm_ready_summary: dict    # {agent, signal, finding} max 200 chars
    data_freshness: str        # ISO timestamp of most recent data point
    execution_time_ms: int
    error: str | None          # set if agent raised exception
```

---

## Implementation Checklist

For each agent implementation:

- [ ] Fetch required data (from collector or context dict)
- [ ] Handle `DataUnavailableError` — return neutral signal with 0.0 confidence
- [ ] Compute signal score using documented methodology
- [ ] Set `signal` based on score thresholds: Bullish (≥60), Bearish (≤40), else Neutral
- [ ] Build `bullish_factors` list with at least 1 data-backed point
- [ ] Build `bearish_factors` list with at least 1 data-backed point
- [ ] Set `supporting_data` with all raw values used in computation
- [ ] Set `llm_ready_summary.finding` to max 200 characters
- [ ] Set `data_freshness` to ISO timestamp of most recent data
- [ ] Validate output passes `BaseAgent.validate_output()`
- [ ] Write unit test in `tests/unit/test_agent_{id}.py`

---

## Score Thresholds

| Score Range | Signal   | Meaning                   |
|-------------|----------|---------------------------|
| 75–100      | Bullish  | Strong bullish evidence   |
| 60–74       | Bullish  | Moderate bullish evidence |
| 41–59       | Neutral  | No clear direction        |
| 26–40       | Bearish  | Moderate bearish evidence |
| 0–25        | Bearish  | Strong bearish evidence   |

---

## Data Access Patterns

### From Collectors (Tier 1 agents)
```python
from modules.market_data.collectors.yahoo_collector import YahooFinanceCollector
collector = YahooFinanceCollector()
df = collector.fetch_with_fallback(symbol, start_date="2024-01-01")
```

### From Context (dependency agents)
```python
def run(self, symbol: str, context: dict) -> AgentOutput:
    agent1_output = context.get(1)  # Agent 1 output
    if agent1_output and not agent1_output.error:
        regime = agent1_output.supporting_data.get("regime")
```

### From Parquet (historical OHLCV)
```python
from modules.market_data.service import MarketDataService
service = MarketDataService(db=None)  # cache-only mode
df = service.load_parquet(symbol, timeframe="daily")
```

---

## Agent Category Weights

Per SPEC Section 13.2 — Signal Aggregation Agent 30:

| Category          | Base Weight |
|-------------------|-------------|
| Direction         | 0.25        |
| News & Macro      | 0.20        |
| Institutional     | 0.20        |
| Strength          | 0.15        |
| Exit & Reversal   | 0.10        |
| Commodity         | 0.10        |

Individual agent weights within each category are calibrated by historical accuracy.

---

## Adding a New Agent

1. Create `backend/modules/agents/{category}/agent_{id}_{name}.py`
2. Implement `run()` method following the checklist above
3. Register in `backend/modules/agents/registry.py`
4. Add to appropriate execution group in `backend/modules/agents/engine.py`
5. Write unit test in `backend/tests/unit/test_agent_{id}.py`
6. Update `docs/SPEC.md` Section 12 if adding beyond 42
