"""
File path: backend/modules/performance/service.py
Purpose: PerformanceService — resolves expired predictions and tracks live accuracy.

DATA SOURCE NOTE: like Backtesting, the source predictions are the persisted
Agent 33 (Final Prediction Engine) AgentOutput rows. resolve_expired_predictions()
is the first place in the codebase that actually materializes rows into the
`predictions` and `prediction_performance` tables (both existed in the schema
but were never written to before this) — it's the bridge between "live agent
output" and "durable, queryable prediction history."

Calibration report groups predictions by confidence bucket:
  50-60%, 60-70%, 70-80%, 80-90%, 90-100%
"""
import logging
from datetime import date, datetime, timedelta

import numpy as np
from sqlalchemy.orm import Session

logger = logging.getLogger("app")

CONFIDENCE_BUCKETS = [(50, 60), (60, 70), (70, 80), (80, 90), (90, 100)]


class PerformanceService:
    def __init__(self, db: Session, cache=None):
        self.db = db
        self.cache = cache

    # ── Resolution ───────────────────────────────────────────────────────────
    def resolve_expired_predictions(self) -> int:
        """
        Find matured (prediction_date + horizon_days <= today) horizon
        predictions inside historical Agent 33 outputs that haven't been
        materialized into the `predictions` table yet, resolve their actual
        outcome via OHLCV, and persist both a Prediction and a
        PredictionPerformance row. Returns count of predictions resolved.
        """
        from modules.agents.models import AgentOutput as AgentOutputModel
        from modules.predictions.models import Prediction
        from modules.performance.models import PredictionPerformance
        from modules.market_data.service import MarketDataService

        today = date.today()
        # Only need outputs old enough that *any* horizon (min 2 days) could have matured
        cutoff = datetime.combine(today - timedelta(days=2), datetime.min.time())
        rows = (
            self.db.query(AgentOutputModel)
            .filter(AgentOutputModel.agent_id == 33, AgentOutputModel.created_at <= cutoff)
            .all()
        )

        resolved_count = 0
        ohlcv_cache = {}
        svc = MarketDataService()

        for row in rows:
            preds = (row.supporting_data or {}).get("predictions", [])
            prediction_date = row.created_at.date()

            for p in preds:
                horizon_days = p.get("horizon_days")
                expiry_date = prediction_date + timedelta(days=horizon_days)
                if expiry_date > today:
                    continue  # not matured yet

                # Dedup: has this exact (symbol, prediction_date, horizon) already been persisted?
                existing = (
                    self.db.query(Prediction)
                    .filter(
                        Prediction.symbol == row.symbol,
                        Prediction.prediction_date == prediction_date,
                        Prediction.horizon_days == horizon_days,
                    )
                    .first()
                )
                if existing is not None and existing.status == "expired":
                    continue

                if row.symbol not in ohlcv_cache:
                    try:
                        ohlcv_cache[row.symbol] = svc.get_ohlcv(row.symbol, period="2y")
                    except Exception as e:
                        logger.warning(f"Could not load OHLCV for {row.symbol} resolution: {e}")
                        ohlcv_cache[row.symbol] = None
                ohlcv = ohlcv_cache[row.symbol]
                if ohlcv is None or ohlcv.empty:
                    continue

                entry_price, exit_price = self._entry_exit_prices(ohlcv, prediction_date, expiry_date)
                if entry_price is None or exit_price is None:
                    continue

                actual_move_pct = (exit_price - entry_price) / entry_price * 100
                actual_direction = (
                    "Bullish" if actual_move_pct > 0.1 else
                    "Bearish" if actual_move_pct < -0.1 else "Neutral"
                )
                is_correct = p["direction"] == actual_direction

                if existing is None:
                    pred_row = Prediction(
                        symbol=row.symbol,
                        prediction_date=prediction_date,
                        horizon_days=horizon_days,
                        direction=p["direction"],
                        confidence_score=p.get("confidence", 0),
                        risk_score=100 - p.get("confidence", 0),
                        expected_move_pct=p.get("expected_return_pct"),
                        expiry_date=expiry_date,
                        agent_run_id=None,
                    )
                    self.db.add(pred_row)
                    self.db.flush()
                else:
                    pred_row = existing

                pred_row.actual_direction = actual_direction
                pred_row.is_correct = is_correct
                pred_row.status = "expired"

                perf = (
                    self.db.query(PredictionPerformance)
                    .filter(PredictionPerformance.prediction_id == pred_row.id)
                    .first()
                )
                if perf is None:
                    perf = PredictionPerformance(
                        prediction_id=pred_row.id,
                        symbol=row.symbol,
                        horizon_days=horizon_days,
                        predicted_direction=p["direction"],
                        actual_direction=actual_direction,
                        is_correct=is_correct,
                        predicted_confidence=p.get("confidence", 0),
                        predicted_move_pct=p.get("expected_return_pct"),
                        actual_move_pct=actual_move_pct,
                        entry_price=entry_price,
                        exit_price=exit_price,
                        resolved_at=datetime.utcnow(),
                    )
                    self.db.add(perf)
                resolved_count += 1

        self.db.commit()
        return resolved_count

    @staticmethod
    def _entry_exit_prices(ohlcv, entry_date: date, exit_date: date):
        df = ohlcv.copy()
        df["_date"] = (df["date"] if "date" in df.columns else df.index)
        df["_date"] = df["_date"].apply(lambda d: d.date() if hasattr(d, "date") else d)
        close_by_date = dict(zip(df["_date"], df["close"].astype(float)))
        all_dates = sorted(close_by_date.keys())

        def nearest(target, forward_only=False):
            if target in close_by_date:
                return close_by_date[target]
            candidates = [d for d in all_dates if d >= target] if forward_only else all_dates
            if not candidates:
                return None
            nearest_d = min(candidates, key=lambda d: abs((d - target).days))
            if abs((nearest_d - target).days) > 5:
                return None
            return close_by_date[nearest_d]

        return nearest(entry_date), nearest(exit_date, forward_only=True)

    # ── Read endpoints ───────────────────────────────────────────────────────
    def get_accuracy_summary(self, symbol: str = None, horizon: int = None, days: int = 30) -> dict:
        from modules.performance.models import PredictionPerformance
        cutoff = datetime.utcnow() - timedelta(days=days)
        q = self.db.query(PredictionPerformance).filter(PredictionPerformance.resolved_at >= cutoff)
        if symbol:
            q = q.filter(PredictionPerformance.symbol == symbol.upper())
        if horizon:
            q = q.filter(PredictionPerformance.horizon_days == horizon)
        rows = q.all()

        total = len(rows)
        correct = sum(1 for r in rows if r.is_correct)
        accuracy_pct = 100.0 * correct / total if total else 0.0

        bullish = [r for r in rows if r.predicted_direction == "Bullish"]
        bearish = [r for r in rows if r.predicted_direction == "Bearish"]
        bullish_acc = 100.0 * sum(1 for r in bullish if r.is_correct) / len(bullish) if bullish else 0.0
        bearish_acc = 100.0 * sum(1 for r in bearish if r.is_correct) / len(bearish) if bearish else 0.0

        by_horizon = []
        for h in sorted({r.horizon_days for r in rows}):
            h_rows = [r for r in rows if r.horizon_days == h]
            h_correct = sum(1 for r in h_rows if r.is_correct)
            h_total = len(h_rows)
            by_horizon.append({
                "horizon_days": h,
                "total_predictions": h_total,
                "correct_predictions": h_correct,
                "win_rate": round(h_correct / h_total, 4) if h_total else 0.0,
                "accuracy_pct": round(100.0 * h_correct / h_total, 2) if h_total else 0.0,
            })

        return {
            "total_predictions": total,
            "correct_predictions": correct,
            "accuracy_pct": round(accuracy_pct, 2),
            "win_rate": round(correct / total, 4) if total else 0.0,
            "overall_win_rate": round(correct / total, 4) if total else 0.0,
            "bullish_accuracy_pct": round(bullish_acc, 2),
            "bearish_accuracy_pct": round(bearish_acc, 2),
            "period_days": days,
            "by_horizon": by_horizon,
        }

    def get_calibration_report(self) -> dict:
        from modules.performance.models import PredictionPerformance
        rows = self.db.query(PredictionPerformance).all()
        buckets = {}
        for lo, hi in CONFIDENCE_BUCKETS:
            bucket_rows = [r for r in rows if lo <= r.predicted_confidence < hi]
            if not bucket_rows:
                buckets[f"{lo}-{hi}"] = {"predicted": (lo + hi) / 2, "actual": None, "count": 0}
                continue
            actual_acc = 100.0 * sum(1 for r in bucket_rows if r.is_correct) / len(bucket_rows)
            avg_predicted = float(np.mean([r.predicted_confidence for r in bucket_rows]))
            buckets[f"{lo}-{hi}"] = {
                "predicted": round(avg_predicted, 2),
                "actual": round(actual_acc, 2),
                "count": len(bucket_rows),
            }

        scored = [(b["predicted"], b["actual"]) for b in buckets.values() if b["actual"] is not None]
        overall_calibration_error = (
            round(float(np.mean([abs(p - a) for p, a in scored])), 2) if scored else 0.0
        )
        return {"buckets": buckets, "overall_calibration_error": overall_calibration_error}

    def get_resolved_history(self, symbol: str = None, limit: int = 50) -> list:
        from modules.performance.models import PredictionPerformance
        q = self.db.query(PredictionPerformance).order_by(PredictionPerformance.resolved_at.desc())
        if symbol:
            q = q.filter(PredictionPerformance.symbol == symbol.upper())
        return q.limit(limit).all()