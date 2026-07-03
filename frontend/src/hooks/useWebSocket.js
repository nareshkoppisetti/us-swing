/**
 * File: frontend/src/hooks/useWebSocket.js
 * WebSocket hook — two calling conventions supported:
 *
 *   1. useWebSocket()              → returns { subscribe, isConnected }
 *   2. useWebSocket(symbol, opts)  → legacy: subscribes to agent_updates for symbol
 *      opts.onAgentUpdate(msg) called when an agent result arrives for symbol
 *
 * SPEC Section 16.2 — WebSocket channels
 */
'use client';
import { useEffect, useCallback, useRef } from 'react';
import { getCookie } from '@/lib/api';
import wsManager from '@/lib/websocket';

export function useWebSocket(symbol, opts) {
  const connectedRef = useRef(false);

  // Ensure WS is connected on mount
  useEffect(() => {
    if (typeof window === 'undefined' || !wsManager) return;
    if (!connectedRef.current) {
      const token = getCookie('usa-swing-token');
      if (token) { wsManager.connect(token); connectedRef.current = true; }
    }
  }, []);

  // Legacy mode: useWebSocket(symbol, { onAgentUpdate })
  useEffect(() => {
    if (!symbol || !opts?.onAgentUpdate || !wsManager) return;
    const unsub = wsManager.subscribe('agent_updates', (data) => {
      if (data.symbol === symbol) opts.onAgentUpdate(data);
    });
    return unsub;
  }, [symbol, opts?.onAgentUpdate]);

  const subscribe = useCallback((channel, callback) => {
    if (!wsManager) return () => {};
    const token = getCookie('usa-swing-token');
    if (token && !wsManager.isConnected) wsManager.connect(token);
    return wsManager.subscribe(channel, callback);
  }, []);

  return { subscribe, isConnected: wsManager?.isConnected ?? false };
}

export default useWebSocket;
