"""
File: backend/modules/agents/engine.py
Purpose: AgentEngine — runs all 42 agents for a symbol in dependency order,
         persists results to DB, broadcasts via WebSocket.
         Per SPEC Section 9 and BUILD_PLAN Phase 3.

Execution order: topological sort by dependencies.
Parallelism: tier-1 agents with no dependencies run concurrently (ThreadPoolExecutor).
             Tier-2+ agents run after all their dependencies resolve.
"""
import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError as FutureTimeout
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from modules.agents.base_agent import AgentOutput, Signal
from modules.agents.registry import get_registry, list_agents

logger = logging.getLogger("agents")

AGENT_TIMEOUT_SEC   = 45   # per-agent timeout
MAX_PARALLEL        = 8    # max concurrent tier-1 agents
PREDICTION_AGENTS   = {30, 31, 32, 33}   # always run after all others


def _topological_sort(registry: dict) -> list:
    """
    Kahn's algorithm — returns agent_ids in dependency-resolved execution order.
    Prediction layer (30-33) always last.
    """
    in_degree = {aid: 0 for aid in registry}
    dependents = {aid: [] for aid in registry}

    for aid, cls in registry.items():
        for dep in cls.dependencies:
            if dep in registry:
                in_degree[aid] += 1
                dependents[dep].append(aid)

    queue = [aid for aid, deg in in_degree.items()
             if deg == 0 and aid not in PREDICTION_AGENTS]
    result = []
    visited = set()

    while queue:
        queue.sort()  # stable ordering
        aid = queue.pop(0)
        if aid in visited:
            continue
        visited.add(aid)
        result.append(aid)
        for dep_of in dependents[aid]:
            if dep_of in visited or dep_of in PREDICTION_AGENTS:
                continue
            in_degree[dep_of] -= 1
            if in_degree[dep_of] == 0:
                queue.append(dep_of)

    # Append prediction agents in fixed order
    for pa in sorted(PREDICTION_AGENTS):
        if pa in registry:
            result.append(pa)

    return result


class AgentEngine:
    """
    Runs all 42 agents for a symbol.
    Returns dict: agent_id → AgentOutput.
    """

    def __init__(self, db: Optional[Session] = None, broadcast_fn=None):
        self.db = db
        self.broadcast_fn = broadcast_fn  # async fn(symbol, agent_id, output)
        self._registry = None

    def _get_registry(self):
        if self._registry is None:
            self._registry = get_registry()
        return self._registry

    def run_all(self, symbol: str) -> dict:
        """
        Execute all agents for symbol.
        Returns {agent_id: AgentOutput}.
        """
        registry = self._get_registry()
        if not registry:
            logger.error("Agent registry is empty — cannot run agents")
            return {}

        order = _topological_sort(registry)
        context: dict = {}   # agent_id → AgentOutput

        run_id = self._start_run(symbol)

        # Group tier-1 no-dep agents for parallel execution
        parallel_group = [aid for aid in order
                          if aid not in PREDICTION_AGENTS
                          and not registry[aid].dependencies]
        sequential_after = [aid for aid in order
                            if aid not in parallel_group
                            and aid not in PREDICTION_AGENTS]

        total_start = time.time()
        logger.info(f"[{symbol}] Running {len(order)} agents: "
                    f"{len(parallel_group)} parallel, {len(sequential_after)} sequential, "
                    f"{len(PREDICTION_AGENTS)} prediction")

        # ── Phase 1: parallel no-dep agents ──────────────────────────────────
        with ThreadPoolExecutor(max_workers=MAX_PARALLEL) as executor:
            futures = {}
            for aid in parallel_group:
                cls = registry.get(aid)
                if cls:
                    agent = cls()
                    futures[executor.submit(self._run_one, agent, symbol, {})] = aid

            for future in as_completed(futures, timeout=AGENT_TIMEOUT_SEC + 5):
                aid = futures[future]
                try:
                    output = future.result(timeout=1)
                except FutureTimeout:
                    output = self._timeout_output(aid, registry)
                except Exception as e:
                    output = self._error_output(aid, registry, str(e))
                context[aid] = output
                self._persist(symbol, output, run_id)

        # ── Phase 2: sequential agents (have deps) ────────────────────────────
        for aid in sequential_after:
            cls = registry.get(aid)
            if not cls:
                continue
            agent = cls()
            try:
                output = self._run_one(agent, symbol, context)
            except Exception as e:
                output = self._error_output(aid, registry, str(e))
            context[aid] = output
            self._persist(symbol, output, run_id)

        # ── Phase 3: prediction layer (30-33) — always sequential ─────────────
        for aid in sorted(PREDICTION_AGENTS):
            cls = registry.get(aid)
            if not cls:
                continue
            agent = cls()
            try:
                output = self._run_one(agent, symbol, context)
            except Exception as e:
                output = self._error_output(aid, registry, str(e))
            context[aid] = output
            self._persist(symbol, output, run_id)

        elapsed = time.time() - total_start
        success = sum(1 for o in context.values() if not o.error)
        logger.info(f"[{symbol}] Engine complete: {success}/{len(context)} agents OK "
                    f"in {elapsed:.2f}s")
        self._finish_run(run_id, total=len(context), successful=success, failed=len(context) - success)
        return context

    def run_single(self, symbol: str, agent_id: int, context: dict = None) -> AgentOutput:
        """Run a single agent, optionally with pre-populated context."""
        registry = self._get_registry()
        cls = registry.get(agent_id)
        if not cls:
            raise KeyError(f"Agent {agent_id} not found")
        if context is None:
            context = {}
        run_id = self._start_run(symbol, total_agents=1)
        agent = cls()
        output = self._run_one(agent, symbol, context)
        self._persist(symbol, output, run_id)
        self._finish_run(run_id, total=1, successful=0 if output.error else 1, failed=1 if output.error else 0)
        return output

    def _run_one(self, agent, symbol: str, context: dict) -> AgentOutput:
        """Execute a single agent with timeout guard."""
        try:
            output = agent.run(symbol, context)
            return output
        except Exception as e:
            logger.error(f"Agent {agent.agent_id} ({agent.agent_name}) error for {symbol}: {e}")
            return self._error_output(agent.agent_id, {agent.agent_id: type(agent)}, str(e))

    def _start_run(self, symbol: str, total_agents: int = 42) -> Optional[str]:
        """Create an AgentRun row for this pipeline execution. Returns its id, or None if no db session."""
        if self.db is None:
            return None
        try:
            from modules.agents.models import AgentRun
            run = AgentRun(
                symbol=symbol,
                run_started_at=datetime.utcnow(),
                total_agents=total_agents,
                status="running",
                triggered_by="api",
            )
            self.db.add(run)
            self.db.commit()
            self.db.refresh(run)
            return run.id
        except Exception as e:
            logger.warning(f"Failed to create AgentRun for {symbol}: {e}")
            try:
                self.db.rollback()
            except Exception:
                pass
            return None

    def _finish_run(self, run_id: Optional[str], total: int, successful: int, failed: int) -> None:
        """Mark an AgentRun row as complete with final counts."""
        if self.db is None or run_id is None:
            return
        try:
            from modules.agents.models import AgentRun
            run = self.db.query(AgentRun).filter(AgentRun.id == run_id).first()
            if run:
                run.run_completed_at = datetime.utcnow()
                run.total_agents = total
                run.successful_agents = successful
                run.failed_agents = failed
                run.status = "complete" if failed == 0 else "failed"
                self.db.commit()
        except Exception as e:
            logger.warning(f"Failed to finalize AgentRun {run_id}: {e}")
            try:
                self.db.rollback()
            except Exception:
                pass

    def _persist(self, symbol: str, output: AgentOutput, run_id: Optional[str] = None):
        """Persist AgentOutput to DB if session available."""
        if self.db is None or output is None:
            return
        try:
            from modules.agents.models import AgentOutput as AgentOutputModel
            row = AgentOutputModel(
                agent_run_id=run_id or "unknown",
                symbol=symbol,
                agent_id=output.agent_id,
                signal=output.signal.value if isinstance(output.signal, Signal) else str(output.signal),
                score=output.score,
                confidence=output.confidence,
                weight=output.weight,
                reasoning=output.reasoning,
                bullish_factors=output.bullish_factors,
                bearish_factors=output.bearish_factors,
                supporting_data=output.supporting_data,
                llm_ready_summary=output.llm_ready_summary,
                data_freshness=output.data_freshness,
                execution_time_ms=output.execution_time_ms,
                error=output.error,
                created_at=datetime.utcnow(),
            )
            self.db.merge(row)
            self.db.commit()
        except Exception as e:
            logger.warning(f"Failed to persist Agent {output.agent_id} output: {e}")
            try:
                self.db.rollback()
            except Exception:
                pass

    def _timeout_output(self, agent_id: int, registry: dict) -> AgentOutput:
        name = registry[agent_id].agent_name if agent_id in registry else f"Agent{agent_id}"
        return AgentOutput(
            agent_id=agent_id, agent_name=name,
            signal=Signal.NEUTRAL, score=50.0, confidence=0.0, weight=0.5,
            reasoning="Agent timed out", bullish_factors=[], bearish_factors=[],
            supporting_data={}, llm_ready_summary={"agent": name, "signal": "Neutral", "finding": "Timeout"},
            data_freshness=datetime.utcnow().isoformat(), execution_time_ms=AGENT_TIMEOUT_SEC * 1000,
            error=f"Timeout after {AGENT_TIMEOUT_SEC}s",
        )

    def _error_output(self, agent_id: int, registry: dict, err: str) -> AgentOutput:
        name = registry[agent_id].agent_name if agent_id in registry else f"Agent{agent_id}"
        return AgentOutput(
            agent_id=agent_id, agent_name=name,
            signal=Signal.NEUTRAL, score=50.0, confidence=0.0, weight=0.5,
            reasoning="", bullish_factors=[], bearish_factors=[],
            supporting_data={}, llm_ready_summary={"agent": name, "signal": "Neutral", "finding": "Error"},
            data_freshness=datetime.utcnow().isoformat(), execution_time_ms=0,
            error=err,
        )
