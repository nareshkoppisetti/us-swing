"""
File: backend/core/websocket_manager.py
Purpose: ConnectionManager for WebSocket broadcasting.
         Per SPEC Section 8: real-time agent updates pushed to subscribed clients.
"""
import asyncio
import json
import logging
from typing import Dict, Set

from fastapi import WebSocket

logger = logging.getLogger("app")


class ConnectionManager:
    """
    Manages active WebSocket connections.
    Clients subscribe to symbols: {symbol: set of websockets}.
    """
    def __init__(self):
        self.connections: Dict[str, Set[WebSocket]] = {}
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket, symbol: str):
        await websocket.accept()
        symbol = symbol.upper()
        if symbol not in self.connections:
            self.connections[symbol] = set()
        self.connections[symbol].add(websocket)
        logger.info(f"WS connected: {symbol} ({len(self.connections[symbol])} clients)")

    async def disconnect(self, websocket: WebSocket, symbol: str):
        symbol = symbol.upper()
        if symbol in self.connections:
            self.connections[symbol].discard(websocket)
            if not self.connections[symbol]:
                del self.connections[symbol]

    async def broadcast_agent_update(self, symbol: str, agent_id: int, output):
        """Broadcast a single agent result to all subscribers of symbol."""
        symbol = symbol.upper()
        if symbol not in self.connections:
            return
        payload = json.dumps({
            "type":       "agent_update",
            "symbol":     symbol,
            "agent_id":   agent_id,
            "agent_name": output.agent_name,
            "signal":     output.signal.value if hasattr(output.signal, "value") else str(output.signal),
            "score":      output.score,
            "confidence": output.confidence,
            "error":      output.error,
            "timestamp":  output.data_freshness,
        })
        dead = set()
        for ws in list(self.connections[symbol]):
            try:
                await ws.send_text(payload)
            except Exception:
                dead.add(ws)
        for ws in dead:
            self.connections[symbol].discard(ws)

    async def broadcast_prediction(self, symbol: str, prediction: dict):
        """Broadcast final prediction (Agent 33 output) to subscribers."""
        symbol = symbol.upper()
        if symbol not in self.connections:
            return
        payload = json.dumps({
            "type":    "prediction_update",
            "symbol":  symbol,
            **prediction,
        })
        dead = set()
        for ws in list(self.connections.get(symbol, set())):
            try:
                await ws.send_text(payload)
            except Exception:
                dead.add(ws)
        for ws in dead:
            self.connections[symbol].discard(ws)

    async def broadcast_to_all(self, message: dict):
        """Broadcast a message to all connected clients."""
        payload = json.dumps(message)
        for symbol, clients in list(self.connections.items()):
            dead = set()
            for ws in list(clients):
                try:
                    await ws.send_text(payload)
                except Exception:
                    dead.add(ws)
            for ws in dead:
                self.connections[symbol].discard(ws)

    def active_symbols(self) -> list:
        return list(self.connections.keys())

    def total_connections(self) -> int:
        return sum(len(v) for v in self.connections.values())


# Singleton
ws_manager = ConnectionManager()
