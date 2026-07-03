"""
File path: backend/modules/signals/service.py
Purpose: SignalService — derives tradeable signals from predictions and manages their lifecycle.
         Uses TradeSignal model (renamed from Signal to avoid clash with agents Signal enum).
"""
import logging
from sqlalchemy.orm import Session
from modules.signals.models import TradeSignal

logger = logging.getLogger("app")

SIGNAL_CONFIDENCE_THRESHOLD = 65.0


class SignalService:
    def __init__(self, db: Session, cache=None):
        self.db = db
        self.cache = cache

    def generate_signal(self, prediction) -> TradeSignal | None:
        """
        Generate a TradeSignal from a Prediction if confidence >= threshold.
        Returns None if confidence too low.
        TODO: Implement
        """
        raise NotImplementedError

    def compute_entry_levels(self, symbol: str, direction: str, atr: float, current_price: float) -> dict:
        """
        Compute entry, stop, target levels using ATR-based method.
        Returns {entry, stop, target_1, target_2, risk_reward_ratio}
        TODO: Implement
        """
        raise NotImplementedError

    def get_active_signals(self, symbol: str = None) -> list[TradeSignal]:
        """Fetch all active signals, optionally filtered by symbol. TODO."""
        raise NotImplementedError

    def invalidate_signal(self, signal_id: str, reason: str) -> None:
        """Mark a TradeSignal as inactive with an invalidation reason. TODO."""
        raise NotImplementedError
