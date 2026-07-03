"""
File path: backend/modules/alerts/delivery.py
Purpose: AlertDeliveryService — dispatches alert notifications via configured channels.
Called by AlertService.trigger_alert() when an alert condition is met.

Delivery channels (per SPEC):
  - In-app: broadcast "alert_triggered" event via WebSocket
  - Email: send plain-text email via SMTP (configurable)

MVP delivery stack:
  - WebSocket: FastAPI WebSocket manager (in-memory, single process). Connections
    are tracked per-symbol (not per-user), so in-app delivery broadcasts to all
    subscribers of the alert's symbol with the owning user_id included in the
    payload — the frontend filters client-side to the logged-in user.
  - Email: SMTP via Python smtplib. Config keys (SMTP_HOST, SMTP_PORT,
    SMTP_USER, SMTP_PASSWORD, SMTP_FROM_ADDRESS) are NOT currently defined in
    config.py — if unset, email delivery is skipped with a logged warning
    rather than failing the whole alert trigger.
"""
import logging
import smtplib
from email.mime.text import MIMEText

logger = logging.getLogger("app")


class AlertDeliveryService:
    """Dispatches alert notifications to configured channels."""

    def __init__(self, websocket_manager=None):
        if websocket_manager is None:
            from core.websocket_manager import ws_manager
            websocket_manager = ws_manager
        self.websocket_manager = websocket_manager

    async def deliver(self, alert: object, event_data: dict) -> dict:
        """Dispatch alert notification to all enabled channels."""
        delivered_via = []
        errors = []

        if getattr(alert, "notify_in_app", False):
            try:
                await self._deliver_websocket(alert, event_data)
                delivered_via.append("in_app")
            except Exception as e:
                logger.error(f"WebSocket delivery failed for alert {alert.id}: {e}")
                errors.append(f"in_app: {e}")

        if getattr(alert, "notify_email", False):
            try:
                sent = await self._deliver_email(alert, event_data)
                if sent:
                    delivered_via.append("email")
                else:
                    errors.append("email: SMTP not configured — skipped")
            except Exception as e:
                logger.error(f"Email delivery failed for alert {alert.id}: {e}")
                errors.append(f"email: {e}")

        return {"delivered_via": delivered_via, "errors": errors}

    async def _deliver_websocket(self, alert: object, event_data: dict) -> None:
        """Broadcast alert_triggered event to subscribers of the alert's symbol."""
        await self.websocket_manager.broadcast_to_all({
            "type": "alert_triggered",
            "data": {
                "alert_id": alert.id,
                "user_id": alert.user_id,
                "symbol": alert.symbol,
                "alert_type": alert.alert_type,
                "message": self._build_message(alert, event_data),
                "event_data": event_data,
            },
        })

    async def _deliver_email(self, alert: object, event_data: dict) -> bool:
        """
        Send plain-text email notification via SMTP.
        Returns False (no-op, not an error) if SMTP isn't configured.
        """
        from config import settings
        host = getattr(settings, "SMTP_HOST", None)
        port = getattr(settings, "SMTP_PORT", None)
        user = getattr(settings, "SMTP_USER", None)
        password = getattr(settings, "SMTP_PASSWORD", None)
        from_addr = getattr(settings, "SMTP_FROM_ADDRESS", None)
        to_addr = getattr(alert, "user_email", None)

        if not all([host, port, from_addr]):
            logger.info(f"Alert {alert.id}: SMTP not configured in .env, skipping email delivery.")
            return False
        if not to_addr:
            logger.info(f"Alert {alert.id}: no recipient email available, skipping email delivery.")
            return False

        subject = f"USA Swing Alert: {alert.symbol} — {alert.alert_type}"
        body = self._build_message(alert, event_data)
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = from_addr
        msg["To"] = to_addr

        with smtplib.SMTP_SSL(host, int(port)) as server:
            if user and password:
                server.login(user, password)
            server.sendmail(from_addr, [to_addr], msg.as_string())
        return True

    @staticmethod
    def _build_message(alert: object, event_data: dict) -> str:
        return (
            f"Alert triggered for {alert.symbol} ({alert.alert_type}).\n"
            f"Threshold: {getattr(alert, 'threshold_value', None)}\n"
            f"Event: {event_data}"
        )
