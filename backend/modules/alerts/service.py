"""
File path: backend/modules/alerts/service.py
Purpose: AlertService — manages alert CRUD and evaluation.

Alert evaluation is called by:
  - Scheduler after every prediction run (new_prediction, confidence_above, signal_generated)
  - Market data collector (price_above, price_below)
  - Monitoring service (agent_failure)
"""
import logging
from datetime import datetime

from sqlalchemy.orm import Session

from core.exceptions import NotFoundError, AuthorizationError
from modules.alerts.models import Alert
from modules.auth.models import User

logger = logging.getLogger("app")


class AlertService:
    def __init__(self, db: Session, cache=None):
        self.db = db
        self.cache = cache

    def create_alert(self, user_id: str, symbol: str, alert_type: str, **kwargs) -> Alert:
        alert = Alert(
            user_id=user_id,
            symbol=symbol.upper(),
            alert_type=alert_type,
            threshold_value=kwargs.get("threshold_value"),
            direction_filter=kwargs.get("direction_filter"),
            horizon_filter=kwargs.get("horizon_filter"),
            notify_email=kwargs.get("notify_email", True),
            notify_in_app=kwargs.get("notify_in_app", True),
        )
        self.db.add(alert)
        self.db.commit()
        self.db.refresh(alert)
        return alert

    def get_user_alerts(self, user_id: str) -> list:
        return (
            self.db.query(Alert)
            .filter(Alert.user_id == user_id)
            .order_by(Alert.created_at.desc())
            .all()
        )

    def update_alert(self, alert_id: str, user_id: str, **kwargs) -> Alert:
        alert = self.db.query(Alert).filter(Alert.id == alert_id).first()
        if alert is None:
            raise NotFoundError(f"Alert '{alert_id}' not found")
        if alert.user_id != user_id:
            raise AuthorizationError("You do not own this alert")
        for field in ("threshold_value", "direction_filter", "horizon_filter",
                      "notify_email", "notify_in_app", "is_active"):
            if field in kwargs and kwargs[field] is not None:
                setattr(alert, field, kwargs[field])
        alert.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(alert)
        return alert

    def delete_alert(self, alert_id: str, user_id: str) -> None:
        alert = self.db.query(Alert).filter(Alert.id == alert_id).first()
        if alert is None:
            raise NotFoundError(f"Alert '{alert_id}' not found")
        if alert.user_id != user_id:
            raise AuthorizationError("You do not own this alert")
        self.db.delete(alert)
        self.db.commit()

    # ── Evaluation ───────────────────────────────────────────────────────────
    def evaluate_alerts(self, symbol: str, event_type: str, event_data: dict) -> list:
        """
        Evaluate all active alerts for symbol against the given event.
        event_type: 'price' | 'new_prediction' | 'signal_generated' | 'agent_failure'
        event_data: e.g. {'price': 123.45}, {'confidence': 72.0, 'direction': 'Bullish', 'horizon': '10'},
                    {'agent_id': 16, 'error_rate': 0.4}
        Returns list of triggered alert IDs.
        """
        alerts = (
            self.db.query(Alert)
            .filter(Alert.symbol == symbol.upper(), Alert.is_active == True)  # noqa: E712
            .all()
        )
        triggered_ids = []
        for alert in alerts:
            if self._matches(alert, event_type, event_data):
                self._mark_triggered(alert)
                triggered_ids.append(alert.id)
        return triggered_ids

    @staticmethod
    def _matches(alert: Alert, event_type: str, event_data: dict) -> bool:
        if alert.alert_type == "price_above" and event_type == "price":
            price = event_data.get("price")
            return price is not None and alert.threshold_value is not None and price > alert.threshold_value

        if alert.alert_type == "price_below" and event_type == "price":
            price = event_data.get("price")
            return price is not None and alert.threshold_value is not None and price < alert.threshold_value

        if alert.alert_type == "new_prediction" and event_type == "new_prediction":
            if alert.direction_filter and event_data.get("direction") != alert.direction_filter:
                return False
            if alert.horizon_filter:
                allowed = {h.strip() for h in alert.horizon_filter.split(",")}
                if str(event_data.get("horizon")) not in allowed:
                    return False
            return True

        if alert.alert_type == "confidence_above" and event_type == "new_prediction":
            conf = event_data.get("confidence")
            return conf is not None and alert.threshold_value is not None and conf > alert.threshold_value

        if alert.alert_type == "signal_generated" and event_type == "signal_generated":
            return True

        if alert.alert_type == "agent_failure" and event_type == "agent_failure":
            rate = event_data.get("error_rate")
            return rate is not None and alert.threshold_value is not None and rate > alert.threshold_value

        return False

    def _mark_triggered(self, alert: Alert) -> None:
        alert.last_triggered_at = datetime.utcnow()
        alert.trigger_count = (alert.trigger_count or 0) + 1
        self.db.commit()

    async def trigger_alert(self, alert_id: str, event_data: dict) -> dict:
        """Mark triggered (if not already fresh) and dispatch notifications."""
        from modules.alerts.delivery import AlertDeliveryService
        alert = self.db.query(Alert).filter(Alert.id == alert_id).first()
        if alert is None:
            raise NotFoundError(f"Alert '{alert_id}' not found")

        user = self.db.query(User).filter(User.id == alert.user_id).first()
        alert.user_email = user.email if user else None  # transient attr, not persisted

        self._mark_triggered(alert)
        delivery = AlertDeliveryService()
        result = await delivery.deliver(alert, event_data)
        return result
