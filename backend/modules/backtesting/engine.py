"""
File path: backend/modules/backtesting/engine.py
Purpose: BacktestEngine — replays historical predictions against actual price outcomes.
Per SPEC Section FR-003 and backtesting architecture.

DATA SOURCE NOTE: predictions are read from the already-persisted Agent 33
(Final Prediction Engine) AgentOutput rows for the symbol — the same source
`/predictions/{symbol}` and `/predictions/{symbol}/history` already use.
This backtest therefore evaluates "predictions actually made by this
system while it was running" rather than reconstructing what the agents
*would have* said on arbitrary past dates outside that history — a true
synthetic re-run across arbitrary historical windows would require
re-executing all 42 agents against point-in-time data for every day in
range, which is out of scope here. As you run agents over time, backtest
coverage naturally grows.

Walk-forward methodology actually implemented:
  - Query all persisted Agent 33 outputs for `symbol` where the output's
    created_at date falls in [start_date, end_date]
  - For each one, pull the horizon_days-specific prediction row
  - Look up the actual close price at prediction_date and at
    prediction_date + horizon_days (trading-day approx via calendar days
    since OHLCV is daily-indexed) to determine the realized direction
  - Compare predicted vs actual direction, aggregate metrics
"""
import logging
import math
from datetime import date, datetime, timedelta

import numpy as np
from sqlalchemy.orm import Session

from core.exceptions import DataUnavailableError

logger = logging.getLogger("app")


class BacktestEngine:
    def __init__(self, db: Session, cache=None):
        self.db = db
        self.cache = cache

    def replay(self, symbol: str, start_date: date, end_date: date, horizon_days: int,
               confidence_threshold: float = 65.0) -> dict:
        """Run walk-forward backtest for symbol over date range. Returns metrics dict."""
        from modules.agents.models import AgentOutput as AgentOutputModel
        from modules.market_data.service import MarketDataService

        rows = (
            self.db.query(AgentOutputModel)
            .filter(
                AgentOutputModel.symbol == symbol.upper(),
                AgentOutputModel.agent_id == 33,
                AgentOutputModel.created_at >= datetime.combine(start_date, datetime.min.time()),
                AgentOutputModel.created_at <= datetime.combine(end_date, datetime.max.time()),
            )
            .order_by(AgentOutputModel.created_at)
            .all()
        )
        if not rows:
            raise DataUnavailableError(
                f"No historical predictions found for {symbol} in that date range. "
                f"Run the agent pipeline for {symbol} first (via /agents/run) to build up backtest history."
            )

        svc = MarketDataService()
        try:
            ohlcv = svc.get_ohlcv(symbol.upper(), period="2y")
        except Exception as e:
            raise DataUnavailableError(f"Could not load OHLCV for {symbol} backtest: {e}")
        if ohlcv is None or ohlcv.empty:
            raise DataUnavailableError(f"No OHLCV data available for {symbol}")

        ohlcv = ohlcv.copy()
        ohlcv["date"] = ohlcv["date"] if "date" in ohlcv.columns else ohlcv.index
        ohlcv["date"] = ohlcv["date"].apply(lambda d: d.date() if hasattr(d, "date") else d)
        close_by_date = dict(zip(ohlcv["date"], ohlcv["close"].astype(float)))
        all_dates = sorted(close_by_date.keys())

        predictions, actuals, returns, return_dates = [], [], [], []
        for row in rows:
            preds = (row.supporting_data or {}).get("predictions", [])
            match = next((p for p in preds if p.get("horizon_days") == horizon_days), None)
            if match is None or match.get("confidence", 0) < confidence_threshold:
                continue

            pred_date = row.created_at.date()
            entry_close = self._nearest_close(close_by_date, all_dates, pred_date)
            target_date = pred_date + timedelta(days=horizon_days)
            exit_close = self._nearest_close(close_by_date, all_dates, target_date, forward_only=True)
            if entry_close is None or exit_close is None:
                continue

            actual_return_pct = (exit_close - entry_close) / entry_close * 100
            actual_direction = "Bullish" if actual_return_pct > 0.1 else ("Bearish" if actual_return_pct < -0.1 else "Neutral")

            predictions.append({
                "direction": match["direction"],
                "confidence": match.get("confidence", 0),
                "expected_move_pct": match.get("expected_return_pct", 0),
            })
            actuals.append({
                "actual_direction": actual_direction,
                "actual_move_pct": actual_return_pct,
            })
            # Strategy return: go long if Bullish, short if Bearish, flat if Neutral
            if match["direction"] == "Bullish":
                returns.append(actual_return_pct / 100)
            elif match["direction"] == "Bearish":
                returns.append(-actual_return_pct / 100)
            else:
                returns.append(0.0)
            return_dates.append(pred_date.isoformat())

        if not predictions:
            raise DataUnavailableError(
                f"Found {len(rows)} historical predictions for {symbol}, but none had matured "
                f"enough price history yet to score at the {horizon_days}-day horizon."
            )

        metrics = self.compute_metrics(predictions, actuals)
        metrics["sharpe_ratio"] = self.compute_sharpe(returns)
        equity_curve_values = list(np.cumprod([1 + r for r in returns]))
        metrics["max_drawdown_pct"] = self.compute_max_drawdown(equity_curve_values)
        metrics["total_return_pct"] = (equity_curve_values[-1] - 1) * 100 if equity_curve_values else 0.0
        metrics["equity_curve"] = [
            {"date": d, "cumulative_return": round((v - 1) * 100, 2)}
            for d, v in zip(return_dates, equity_curve_values)
        ]
        return metrics

    @staticmethod
    def _nearest_close(close_by_date: dict, all_dates: list, target: date, forward_only: bool = False):
        """Find the closing price on `target`, or the nearest available trading date."""
        if target in close_by_date:
            return close_by_date[target]
        candidates = [d for d in all_dates if d >= target] if forward_only else all_dates
        if not candidates:
            return None
        nearest = min(candidates, key=lambda d: abs((d - target).days))
        # Don't match to a wildly distant date (e.g. > 5 calendar days off)
        if abs((nearest - target).days) > 5:
            return None
        return close_by_date[nearest]

    def compute_metrics(self, predictions: list, actuals: list) -> dict:
        """Compute accuracy, calibration error, win rate, per-direction accuracy."""
        n = len(predictions)
        correct = [p["direction"] == a["actual_direction"] for p, a in zip(predictions, actuals)]
        accuracy_pct = 100.0 * sum(correct) / n if n else 0.0

        bullish_pairs = [(p, a, c) for p, a, c in zip(predictions, actuals, correct) if p["direction"] == "Bullish"]
        bearish_pairs = [(p, a, c) for p, a, c in zip(predictions, actuals, correct) if p["direction"] == "Bearish"]
        bullish_acc = 100.0 * sum(c for _, _, c in bullish_pairs) / len(bullish_pairs) if bullish_pairs else None
        bearish_acc = 100.0 * sum(c for _, _, c in bearish_pairs) / len(bearish_pairs) if bearish_pairs else None

        avg_confidence = float(np.mean([p["confidence"] for p in predictions])) if n else 0.0
        # Calibration error: |stated confidence - realized accuracy|, both as 0-100 scale
        calibration_error = abs(avg_confidence - accuracy_pct)

        wins = [a["actual_move_pct"] for p, a, c in zip(predictions, actuals, correct)
                if p["direction"] in ("Bullish", "Bearish") and c]
        losses = [a["actual_move_pct"] for p, a, c in zip(predictions, actuals, correct)
                  if p["direction"] in ("Bullish", "Bearish") and not c]
        directional = [p for p in predictions if p["direction"] in ("Bullish", "Bearish")]
        win_rate_pct = 100.0 * len(wins) / len(directional) if directional else 0.0

        return {
            "total_predictions": n,
            "correct_predictions": sum(correct),
            "accuracy_pct": round(accuracy_pct, 2),
            "bullish_accuracy_pct": round(bullish_acc, 2) if bullish_acc is not None else None,
            "bearish_accuracy_pct": round(bearish_acc, 2) if bearish_acc is not None else None,
            "avg_confidence": round(avg_confidence, 2),
            "calibration_error": round(calibration_error, 2),
            "win_rate_pct": round(win_rate_pct, 2),
            "avg_win_pct": round(float(np.mean([abs(w) for w in wins])), 2) if wins else None,
            "avg_loss_pct": round(float(np.mean([abs(l) for l in losses])), 2) if losses else None,
        }

    def compute_sharpe(self, returns: list, risk_free_rate: float = 0.05) -> float:
        """Sharpe ratio = (mean_return - risk_free_per_period) / std_return × sqrt(252)."""
        if not returns or len(returns) < 2:
            return 0.0
        arr = np.array(returns)
        std = arr.std(ddof=1)
        if std == 0 or math.isnan(std):
            return 0.0
        daily_rf = risk_free_rate / 252
        sharpe = (arr.mean() - daily_rf) / std * math.sqrt(252)
        return round(float(sharpe), 3) if not math.isnan(sharpe) else 0.0

    def compute_max_drawdown(self, equity_curve: list) -> float:
        """Max drawdown = max(peak - trough) / peak across equity curve, as a percentage."""
        if not equity_curve:
            return 0.0
        arr = np.array(equity_curve)
        running_max = np.maximum.accumulate(arr)
        drawdowns = (running_max - arr) / running_max
        return round(float(drawdowns.max()) * 100, 2)
