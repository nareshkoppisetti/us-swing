"""
File: backend/modules/predictions/router.py
Endpoints:
  GET /predictions/{symbol}         — latest prediction for symbol
  GET /predictions/{symbol}/history — historical predictions
  POST /predictions/generate        — generate fresh prediction
"""
import logging
from datetime import datetime
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from dependencies import get_db, get_current_user
from modules.agents.engine import AgentEngine
from modules.agents.models import AgentOutput as AgentOutputModel

logger = logging.getLogger("app")
router = APIRouter(tags=["Predictions"])


def _meta():
    return {"request_id": str(uuid4()), "timestamp": datetime.utcnow().isoformat() + "Z"}


def _extract_prediction(symbol: str, db: Session) -> dict:
    """Pull Agent 33 latest output from DB for symbol."""
    from sqlalchemy import desc
    row = (
        db.query(AgentOutputModel)
        .filter_by(symbol=symbol.upper(), agent_id=33)
        .order_by(desc(AgentOutputModel.created_at))
        .first()
    )
    if not row:
        return None

    preds = (row.supporting_data or {}).get("predictions", [])
    return {
        "symbol":      row.symbol,
        "signal":      row.signal,
        "score":       row.score,
        "confidence":  row.confidence,
        "risk_level":  (row.supporting_data or {}).get("risk_level", "Unknown"),
        "is_degraded": (row.supporting_data or {}).get("is_degraded", False),
        "predictions": preds,
        "bullish_factors": row.bullish_factors or [],
        "bearish_factors": row.bearish_factors or [],
        "reasoning":   row.reasoning,
        "generated_at": row.created_at.isoformat() if row.created_at else None,
    }


@router.get("/{symbol}")
def get_prediction(symbol: str, db: Session = Depends(get_db), _=Depends(get_current_user)):
    pred = _extract_prediction(symbol.upper(), db)
    if not pred:
        raise HTTPException(status_code=404, detail=f"No prediction found for {symbol}. Run /agents/run first.")
    return {"success": True, "data": pred, "meta": _meta()}


@router.get("/{symbol}/history")
def get_prediction_history(
    symbol: str,
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    from sqlalchemy import desc
    rows = (
        db.query(AgentOutputModel)
        .filter_by(symbol=symbol.upper(), agent_id=33)
        .order_by(desc(AgentOutputModel.created_at))
        .limit(limit)
        .all()
    )
    history = []
    for row in rows:
        history.append({
            "signal": row.signal, "score": row.score, "confidence": row.confidence,
            "risk_level": (row.supporting_data or {}).get("risk_level", "Unknown"),
            "generated_at": row.created_at.isoformat() if row.created_at else None,
        })
    return {"success": True, "data": {"symbol": symbol.upper(), "history": history}, "meta": _meta()}


@router.post("/generate")
def generate_prediction(
    symbol: str = Query(..., description="Ticker symbol"),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    """Trigger a full agent run and return Agent 33 output."""
    try:
        engine = AgentEngine(db=db)
        results = engine.run_all(symbol.upper())
        a33 = results.get(33)
        if not a33:
            raise HTTPException(status_code=500, detail="Agent 33 did not produce output")
        pred = _extract_prediction(symbol.upper(), db)
        return {"success": True, "data": pred or {}, "meta": _meta()}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"POST /predictions/generate failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
