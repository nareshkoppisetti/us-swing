"""
File: backend/modules/signals/router.py
Endpoints:
  GET /signals/{symbol}        — latest trade signal (from Agent 33)
  GET /signals/history/{symbol}— historical signals
  GET /signals/watchlist        — signals for all watchlist symbols
"""
import logging
from datetime import datetime
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from dependencies import get_db, get_current_user
from modules.agents.models import AgentOutput as AgentOutputModel

logger = logging.getLogger("app")
router = APIRouter(tags=["Signals"])

WATCHLIST = ["SPY","QQQ","AAPL","TSLA","NVDA","MSFT","AMZN","GOOGL","META","NFLX"]

def _meta():
    return {"request_id": str(uuid4()), "timestamp": datetime.utcnow().isoformat() + "Z"}


def _latest_signal(symbol: str, db: Session) -> dict:
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
    horizon_5d = next((p for p in preds if p.get("horizon_days") == 5), {})
    horizon_20d= next((p for p in preds if p.get("horizon_days") == 20), {})
    return {
        "symbol":       row.symbol,
        "signal":       row.signal,
        "score":        row.score,
        "confidence":   row.confidence,
        "risk_level":   (row.supporting_data or {}).get("risk_level","Unknown"),
        "5d_direction": horizon_5d.get("direction","Neutral"),
        "5d_score":     horizon_5d.get("score",50.0),
        "20d_direction":horizon_20d.get("direction","Neutral"),
        "20d_score":    horizon_20d.get("score",50.0),
        "bullish_factors": row.bullish_factors or [],
        "bearish_factors": row.bearish_factors or [],
        "generated_at": row.created_at.isoformat() if row.created_at else None,
    }


@router.get("/watchlist")
def get_watchlist_signals(db: Session = Depends(get_db), _=Depends(get_current_user)):
    """Return latest signals for watchlist symbols."""
    signals = []
    for sym in WATCHLIST:
        s = _latest_signal(sym, db)
        if s:
            signals.append(s)
    return {"success": True, "data": signals, "meta": _meta()}


@router.get("/{symbol}")
def get_signal(symbol: str, db: Session = Depends(get_db), _=Depends(get_current_user)):
    s = _latest_signal(symbol.upper(), db)
    if not s:
        raise HTTPException(status_code=404, detail=f"No signal for {symbol}. Run /agents/run first.")
    return {"success": True, "data": s, "meta": _meta()}


@router.get("/history/{symbol}")
def get_signal_history(
    symbol: str,
    limit: int = Query(30, ge=1, le=200),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    from sqlalchemy import desc
    rows = (
        db.query(AgentOutputModel)
        .filter_by(symbol=symbol.upper(), agent_id=33)
        .order_by(desc(AgentOutputModel.created_at))
        .limit(limit).all()
    )
    history = [
        {"signal": r.signal, "score": r.score, "confidence": r.confidence,
         "generated_at": r.created_at.isoformat() if r.created_at else None}
        for r in rows
    ]
    return {"success": True, "data": {"symbol": symbol.upper(), "history": history}, "meta": _meta()}
