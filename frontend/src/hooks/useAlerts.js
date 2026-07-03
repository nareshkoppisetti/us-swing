'use client';
import { useState, useEffect, useCallback } from 'react';
import api from '@/lib/api';

export function useAlerts(params = {}) {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetch = useCallback(async () => {
    setLoading(true); setError(null);
    try {
      const d = await api.getAlerts(params);
      setAlerts(d.data || []);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, [JSON.stringify(params)]);

  useEffect(() => { fetch(); }, [fetch]);

  const acknowledge = useCallback(async (id) => {
    try {
      await api.acknowledgeAlert(id);
      setAlerts(prev => prev.map(a => a.id === id ? { ...a, status: 'acknowledged' } : a));
    } catch (e) {
      setError(e.message);
    }
  }, []);

  const create = useCallback(async (data) => {
    try {
      const d = await api.createAlert(data);
      await fetch();
      return d.data;
    } catch (e) {
      setError(e.message);
      throw e;
    }
  }, [fetch]);

  return { alerts, loading, error, refetch: fetch, acknowledge, create };
}

export function useAlertsRealtime() {
  // Real-time alerts via WebSocket — see useWebSocket hook usage in components
  return useAlerts({ status: 'active' });
}
