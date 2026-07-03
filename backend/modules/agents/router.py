"""
File: backend/modules/agents/router.py
Purpose: FastAPI router for agent endpoints.
         Registered at /api/v1/agents in main.py.

Endpoints:
  GET  /agents/                     — list all 42 agent definitions
  GET  /agents/{agent_id}           — get single agent definition
  POST /agents/run                  — trigger full agent run for a symbol
  POST /agents/run/{agent_id}       — trigger single agent run
  GET  /agents/results/{symbol}     — get latest results for symbol (from DB)
  GET  /agents/status               — scheduler status
"""
import logging
from datetime import datetime
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel
from sqlalchemy.orm import Session

from dependencies import get_db, get_current_user, require_admin
from modules.agents.registry import list_agents, get_agent
from modules.agents.engine import AgentEngine
from modules.agents.scheduler import get_scheduler_status

logger = logging.getLogger("agents")
router = APIRouter(tags=["Agents"])


def _meta():
    return {"request_id": str(uuid4()), "timestamp": datetime.utcnow().isoformat() + "Z", "version": "1.0"}


class RunAgentsRequest(BaseModel):
    symbol: str
    agent_ids: list = []   # empty = run all


# ── Definitions ───────────────────────────────────────────────────────────────

@router.get("/")
def list_all_agents(_=Depends(get_current_user)):
    """List all 42 agent definitions (id, name, category, deps, tier)."""
    return {"success": True, "data": list_agents(), "meta": _meta()}


@router.get("/status")
def scheduler_status(_=Depends(get_current_user)):
    """Return APScheduler job status."""
    return {"success": True, "data": get_scheduler_status(), "meta": _meta()}


@router.get("/{agent_id}")
def get_agent_def(agent_id: int, _=Depends(get_current_user)):
    """Get a single agent definition by ID."""
    agents = list_agents()
    match = next((a for a in agents if a["agent_id"] == agent_id), None)
    if not match:
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
    return {"success": True, "data": match, "meta": _meta()}


# ── Execution ─────────────────────────────────────────────────────────────────

@router.post("/run")
def run_agents(
    req: RunAgentsRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    """
    Trigger a full (or partial) agent run for a symbol.
    Runs synchronously — returns Agent 33 final prediction.
    For async runs use BackgroundTasks.
    """
    symbol = req.symbol.upper()
    try:
        engine = AgentEngine(db=db)
        results = engine.run_all(symbol)

        # Serialize outputs
        output_data = {}
        for aid, out in results.items():
            output_data[aid] = {
                "agent_id":       out.agent_id,
                "agent_name":     out.agent_name,
                "signal":         out.signal.value if hasattr(out.signal, "value") else str(out.signal),
                "score":          out.score,
                "confidence":     out.confidence,
                "weight":         out.weight,
                "reasoning":      out.reasoning,
                "bullish_factors":out.bullish_factors,
                "bearish_factors":out.bearish_factors,
                "supporting_data":out.supporting_data,
                "execution_time_ms": out.execution_time_ms,
                "error":          out.error,
            }

        a33 = results.get(33)
        final = {
            "symbol":     symbol,
            "signal":     a33.signal.value if a33 and hasattr(a33.signal,"value") else "Neutral",
            "score":      a33.score        if a33 else 50.0,
            "confidence": a33.confidence   if a33 else 0.0,
            "risk_level": (a33.supporting_data.get("risk_level","Unknown") if a33 and not a33.error else "Unknown"),
            "predictions":(a33.supporting_data.get("predictions",[])       if a33 and not a33.error else []),
            "agents":     output_data,
        }
        return {"success": True, "data": final, "meta": _meta()}
    except Exception as e:
        logger.error(f"POST /agents/run failed for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/run/{agent_id}")
def run_single_agent(
    agent_id: int,
    req: RunAgentsRequest,
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    """Run a single agent and return its output."""
    symbol = req.symbol.upper()
    try:
        engine = AgentEngine(db=db)
        output = engine.run_single(symbol, agent_id)
        return {
            "success": True,
            "data": {
                "agent_id":        output.agent_id,
                "agent_name":      output.agent_name,
                "signal":          output.signal.value if hasattr(output.signal, "value") else str(output.signal),
                "score":           output.score,
                "confidence":      output.confidence,
                "reasoning":       output.reasoning,
                "bullish_factors": output.bullish_factors,
                "bearish_factors": output.bearish_factors,
                "supporting_data": output.supporting_data,
                "error":           output.error,
            },
            "meta": _meta(),
        }
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
    except Exception as e:
        logger.error(f"POST /agents/run/{agent_id} failed for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ── Results from DB ───────────────────────────────────────────────────────────

@router.get("/results/{symbol}")
def get_agent_results(
    symbol: str,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    """Return the latest persisted AgentOutput rows for a symbol from DB."""
    try:
        from modules.agents.models import AgentOutput as AgentOutputModel
        from sqlalchemy import desc, func

        # Latest run_id per agent for this symbol
        subq = (
            db.query(
                AgentOutputModel.agent_id,
                func.max(AgentOutputModel.created_at).label("latest"),
            )
            .filter(AgentOutputModel.symbol == symbol.upper())
            .group_by(AgentOutputModel.agent_id)
            .subquery()
        )
        rows = (
            db.query(AgentOutputModel)
            .join(subq, (AgentOutputModel.agent_id == subq.c.agent_id) &
                        (AgentOutputModel.created_at == subq.c.latest))
            .all()
        )

        results = []
        for row in rows:
            results.append({
                "agent_id":        row.agent_id,
                "agent_name":      row.agent_name,
                "signal":          row.signal,
                "score":           row.score,
                "confidence":      row.confidence,
                "weight":          row.weight,
                "reasoning":       row.reasoning,
                "bullish_factors": row.bullish_factors or [],
                "bearish_factors": row.bearish_factors or [],
                "supporting_data": row.supporting_data or {},
                "created_at":      row.created_at.isoformat() if row.created_at else None,
                "error":           row.error,
            })

        return {"success": True, "data": {"symbol": symbol.upper(), "agents": results}, "meta": _meta()}
    except Exception as e:
        logger.error(f"GET /agents/results/{symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
