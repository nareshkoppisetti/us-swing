'use client';
import { useState, useEffect, useCallback } from 'react';
import api from '@/lib/api';

export function useSignals(params = {}) {
  const [signals, setSignals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetch = useCallback(async () => {
    setLoading(true); setError(null);
    try {
      const d = await api.getSignals(params);
      setSignals(d.data || []);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, [JSON.stringify(params)]);

  useEffect(() => { fetch(); }, [fetch]);
  return { signals, loading, error, refetch: fetch };
}
