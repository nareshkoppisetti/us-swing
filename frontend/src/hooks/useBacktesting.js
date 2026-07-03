'use client';
import { useState, useCallback } from 'react';
import api from '@/lib/api';

export function useBacktesting() {
  const [running, setRunning] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const run = useCallback(async (params) => {
    setRunning(true); setError(null);
    try {
      const d = await api.runBacktest(params);
      setResult(d.data);
      return d.data;
    } catch (e) {
      setError(e.message);
      throw e;
    } finally {
      setRunning(false);
    }
  }, []);

  return { run, running, result, error };
}
