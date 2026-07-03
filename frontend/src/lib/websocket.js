/**
 * File: frontend/src/lib/websocket.js
 * WebSocket manager — single persistent connection per session.
 *
 * SPEC Section 16.2 — WebSocket API
 * Channels: market_data, agent_updates, prediction_updates, explanation_ready, alerts, system_health
 */

const WS_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/ws';

class WebSocketManager {
  constructor() {
    this._ws = null;
    this._token = null;
    this._subscribers = {}; // channel → Set<callback>
    this._reconnectTimer = null;
    this._reconnectDelay = 2000;
    this._maxReconnectDelay = 30000;
    this._connected = false;
    this._manualClose = false;
  }

  connect(token) {
    if (this._ws && this._ws.readyState === WebSocket.OPEN) return;
    this._token = token;
    this._manualClose = false;
    this._doConnect();
  }

  _doConnect() {
    if (!this._token) return;
    const url = `${WS_URL}?token=${encodeURIComponent(this._token)}`;
    try {
      this._ws = new WebSocket(url);
    } catch {
      this._scheduleReconnect();
      return;
    }

    this._ws.onopen = () => {
      this._connected = true;
      this._reconnectDelay = 2000;
      // Re-subscribe to all channels
      Object.keys(this._subscribers).forEach(channel => {
        if (this._subscribers[channel]?.size > 0) {
          this._send({ action: 'subscribe', channel });
        }
      });
    };

    this._ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);
        const channel = msg.channel || msg.type;
        if (channel && this._subscribers[channel]) {
          this._subscribers[channel].forEach(cb => cb(msg.data ?? msg));
        }
        // Broadcast to wildcard subscribers
        if (this._subscribers['*']) {
          this._subscribers['*'].forEach(cb => cb(msg));
        }
      } catch {}
    };

    this._ws.onclose = () => {
      this._connected = false;
      if (!this._manualClose) {
        this._scheduleReconnect();
      }
    };

    this._ws.onerror = () => {
      this._connected = false;
    };
  }

  _send(msg) {
    if (this._ws?.readyState === WebSocket.OPEN) {
      this._ws.send(JSON.stringify(msg));
    }
  }

  _scheduleReconnect() {
    if (this._manualClose) return;
    clearTimeout(this._reconnectTimer);
    this._reconnectTimer = setTimeout(() => {
      this._reconnectDelay = Math.min(this._reconnectDelay * 1.5, this._maxReconnectDelay);
      this._doConnect();
    }, this._reconnectDelay);
  }

  /**
   * Subscribe to a channel.
   * Returns an unsubscribe function.
   */
  subscribe(channel, callback) {
    if (!this._subscribers[channel]) {
      this._subscribers[channel] = new Set();
    }
    this._subscribers[channel].add(callback);

    // Send subscribe message if connected
    if (this._connected) {
      this._send({ action: 'subscribe', channel });
    }

    return () => {
      if (this._subscribers[channel]) {
        this._subscribers[channel].delete(callback);
        if (this._subscribers[channel].size === 0) {
          delete this._subscribers[channel];
          if (this._connected) {
            this._send({ action: 'unsubscribe', channel });
          }
        }
      }
    };
  }

  disconnect() {
    this._manualClose = true;
    clearTimeout(this._reconnectTimer);
    if (this._ws) {
      this._ws.close();
      this._ws = null;
    }
    this._connected = false;
  }

  get isConnected() { return this._connected; }
}

// Singleton
export const wsManager = typeof window !== 'undefined' ? new WebSocketManager() : null;
export default wsManager;
