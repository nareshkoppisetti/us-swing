"""
File path: backend/modules/backtesting/router.py
Endpoints (per API.md "Backtesting", mounted at /api/v1/backtesting):
  POST /backtesting/run           — trigger walk-forward backtest
  GET  /backtesting?symbol=       — list all backtest runs
  GET  /backtesting/{id}          — get backtest by ID
  GET  /backtesting/{id}/results  — get backtest performance metrics
"""
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from core.exceptions import NotFoundError
from dependencies import get_db, get_current_user
from modules.backtesting.engine import BacktestEngine
from modules.backtesting.models import Backtest, BacktestResult
from modules.backtesting.schemas import BacktestRequest

router = APIRouter(tags=["Backtesting"])


def _backtest_out(b: Backtest) -> dict:
    return {
        "id": b.id, "name": b.name, "symbol": b.symbol,
        "start_date": b.start_date, "end_date": b.end_date,
        "horizon_days": b.horizon_days, "status": b.status,
        "created_at": b.created_at, "completed_at": b.completed_at,
    }


def _result_out(r: BacktestResult) -> dict:
    return {
        "id": r.id, "backtest_id": r.backtest_id,
        "total_predictions": r.total_predictions, "correct_predictions": r.correct_predictions,
        "accuracy_pct": r.accuracy_pct, "bullish_accuracy_pct": r.bullish_accuracy_pct,
        "bearish_accuracy_pct": r.bearish_accuracy_pct, "avg_confidence": r.avg_confidence,
        "calibration_error": r.calibration_error, "sharpe_ratio": r.sharpe_ratio,
        "max_drawdown_pct": r.max_drawdown_pct, "total_return_pct": r.total_return_pct,
        "win_rate_pct": r.win_rate_pct, "avg_win_pct": r.avg_win_pct, "avg_loss_pct": r.avg_loss_pct,
        "by_horizon": r.by_horizon, "created_at": r.created_at,
    }


@router.post("/run")
def run_backtest(req: BacktestRequest, db: Session = Depends(get_db), user=Depends(get_current_user)):
    backtest = Backtest(
        name=f"{req.symbol} {req.horizon_days}d backtest ({req.start_date} to {req.end_date})",
        symbol=req.symbol.upper(),
        start_date=req.start_date,
        end_date=req.end_date,
        horizon_days=req.horizon_days,
        confidence_threshold=req.confidence_threshold,
        status="running",
        triggered_by="manual",
    )
    db.add(backtest)
    db.commit()
    db.refresh(backtest)

    engine = BacktestEngine(db)
    try:
        metrics = engine.replay(
            req.symbol.upper(), req.start_date, req.end_date, req.horizon_days,
            confidence_threshold=req.confidence_threshold,
        )
        result = BacktestResult(
            backtest_id=backtest.id,
            total_predictions=metrics["total_predictions"],
            correct_predictions=metrics["correct_predictions"],
            accuracy_pct=metrics["accuracy_pct"],
            bullish_accuracy_pct=metrics["bullish_accuracy_pct"],
            bearish_accuracy_pct=metrics["bearish_accuracy_pct"],
            avg_confidence=metrics["avg_confidence"],
            calibration_error=metrics["calibration_error"],
            sharpe_ratio=metrics["sharpe_ratio"],
            max_drawdown_pct=metrics["max_drawdown_pct"],
            total_return_pct=metrics["total_return_pct"],
            win_rate_pct=metrics["win_rate_pct"],
            avg_win_pct=metrics["avg_win_pct"],
            avg_loss_pct=metrics["avg_loss_pct"],
        )
        db.add(result)
        backtest.status = "complete"
        backtest.completed_at = datetime.utcnow()
        db.commit()
        db.refresh(result)
        response_data = _result_out(result)
        response_data["equity_curve"] = metrics.get("equity_curve", [])
        response_data["win_rate"] = round((metrics.get("win_rate_pct") or 0) / 100, 4)
        response_data["total_trades"] = metrics.get("total_predictions")
        return {"success": True, "data": {"backtest": _backtest_out(backtest), "results": response_data}, "meta": {}}
    except Exception as e:
        backtest.status = "failed"
        backtest.completed_at = datetime.utcnow()
        db.commit()
        raise


@router.get("/")
def list_backtests(symbol: str = Query(None), db: Session = Depends(get_db), _=Depends(get_current_user)):
    q = db.query(Backtest)
    if symbol:
        q = q.filter(Backtest.symbol == symbol.upper())
    rows = q.order_by(Backtest.created_at.desc()).all()
    return {"success": True, "data": [_backtest_out(b) for b in rows], "meta": {"count": len(rows)}}


@router.get("/{backtest_id}")
def get_backtest(backtest_id: str, db: Session = Depends(get_db), _=Depends(get_current_user)):
    b = db.query(Backtest).filter(Backtest.id == backtest_id).first()
    if b is None:
        raise NotFoundError(f"Backtest '{backtest_id}' not found")
    return {"success": True, "data": _backtest_out(b), "meta": {}}


@router.get("/{backtest_id}/results")
def get_backtest_results(backtest_id: str, db: Session = Depends(get_db), _=Depends(get_current_user)):
    b = db.query(Backtest).filter(Backtest.id == backtest_id).first()
    if b is None:
        raise NotFoundError(f"Backtest '{backtest_id}' not found")
    result = db.query(BacktestResult).filter(BacktestResult.backtest_id == backtest_id).first()
    if result is None:
        raise NotFoundError(f"No results yet for backtest '{backtest_id}' (status: {b.status})")
    return {"success": True, "data": _result_out(result), "meta": {}}
