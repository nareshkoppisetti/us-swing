"""
File path: backend/core/websocket.py
Purpose: WebSocket connection manager and event broadcaster.
         Provides real-time push events to frontend clients.
         Mounted at /ws in main.py.

SPEC Reference: Section 9.3 (WebSocket Real-Time Updates)
BUILD_PLAN Reference: Phase 1.7

Supported event types (SPEC 9.3):
  new_prediction        — new prediction generated for a symbol
  explanation_ready     — LLM explanation completed
  agent_status_update   — agent health status changed
  alert_triggered       — user alert condition met
  system_health_update  — system metric threshold breached

Authentication:
  Token passed as query param: ws://host/ws?token={access_jwt}
  Validated on connect. Unauthenticated connections receive 'auth_required' then close.
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Dict

from fastapi import WebSocket, WebSocketDisconnect, Query
from fastapi.websockets import WebSocketState

from core.exceptions import AuthenticationError

logger = logging.getLogger("app")


# ── Connection Manager ────────────────────────────────────────────────────────

class WebSocketManager:
    """
    In-memory WebSocket connection registry.
    Single-process safe (asyncio event loop).
    Production upgrade: replace with Redis pub/sub for multi-instance.
    """

    def __init__(self):
        # {connection_id: {"ws": WebSocket, "user_id": str, "connected_at": str}}
        self._connections: Dict[str, dict] = {}

    async def connect(self, websocket: WebSocket, user_id: str) -> str:
        """Accept connection and register. Returns connection_id."""
        await websocket.accept()
        conn_id = str(uuid.uuid4())
        self._connections[conn_id] = {
            "ws": websocket,
            "user_id": user_id,
            "connected_at": datetime.now(timezone.utc).isoformat(),
        }
        logger.info("ws_connect", extra={"conn_id": conn_id, "user_id": user_id})
        return conn_id

    def disconnect(self, conn_id: str) -> None:
        """Remove a connection from the registry."""
        conn = self._connections.pop(conn_id, None)
        if conn:
            user_id = conn.get("user_id")
            logger.info("ws_disconnect", extra={"conn_id": conn_id, "user_id": user_id})

    async def broadcast_all(self, event_type: str, data: dict) -> int:
        """
        Send event to ALL connected clients.
        Returns count of successful sends.
        """
        return await self._send_to(
            connections=list(self._connections.items()),
            event_type=event_type,
            data=data,
        )

    async def broadcast_to_user(self, user_id: str, event_type: str, data: dict) -> int:
        """
        Send event to all connections belonging to a specific user.
        Returns count of successful sends.
        """
        target = [
            (cid, conn) for cid, conn in self._connections.items()
            if conn["user_id"] == user_id
        ]
        return await self._send_to(target, event_type, data)

    async def _send_to(self, connections: list, event_type: str, data: dict) -> int:
        """Internal: send message to a list of (conn_id, conn) pairs. Cleans dead connections."""
        message = json.dumps({
            "type": event_type,
            "data": data,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        dead = []
        sent = 0
        for conn_id, conn in connections:
            ws: WebSocket = conn["ws"]
            try:
                if ws.client_state == WebSocketState.CONNECTED:
                    await ws.send_text(message)
                    sent += 1
                else:
                    dead.append(conn_id)
            except Exception:
                dead.append(conn_id)

        for conn_id in dead:
            self.disconnect(conn_id)

        return sent

    @property
    def connection_count(self) -> int:
        return len(self._connections)

    def get_stats(self) -> dict:
        return {
            "total_connections": len(self._connections),
            "users_online": len({c["user_id"] for c in self._connections.values()}),
        }


# ── Global singleton ──────────────────────────────────────────────────────────

ws_manager = WebSocketManager()


# ── WebSocket endpoint ────────────────────────────────────────────────────────

async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(default=None, description="JWT access token"),
) -> None:
    """
    FastAPI WebSocket endpoint handler.
    Mounted at: app.add_api_websocket_route("/ws", websocket_endpoint)

    Flow:
      1. Validate JWT token from query param
      2. Accept connection and register with ws_manager
      3. Send 'connected' confirmation
      4. Keep alive with 30s ping/pong loop
      5. Clean up on disconnect
    """
    from core.security import decode_access_token

    # Validate token before accepting
    if not token:
        await websocket.accept()
        await websocket.send_text(json.dumps({"type": "auth_required", "data": {}}))
        await websocket.close(code=4001)
        return

    try:
        payload = decode_access_token(token)
        user_id = payload["sub"]
    except AuthenticationError:
        await websocket.accept()
        await websocket.send_text(json.dumps({"type": "auth_failed", "data": {}}))
        await websocket.close(code=4001)
        return

    conn_id = await ws_manager.connect(websocket, user_id)

    try:
        # Send welcome
        await websocket.send_text(json.dumps({
            "type": "connected",
            "data": {"connection_id": conn_id, "user_id": user_id},
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }))

        # Keep-alive loop: wait for messages or send ping every 30s
        while True:
            try:
                msg = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
                if msg == "ping":
                    await websocket.send_text(json.dumps({"type": "pong"}))
            except asyncio.TimeoutError:
                # Send server-initiated ping
                await websocket.send_text(json.dumps({"type": "ping"}))
            except WebSocketDisconnect:
                break

    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger.error("ws_error", extra={"conn_id": conn_id, "error": str(e)})
    finally:
        ws_manager.disconnect(conn_id)
