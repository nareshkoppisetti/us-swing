'use client';
import { useState, useEffect, useCallback } from 'react';
import api from '@/lib/api';

export function useExplanation(predictionId) {
  const [explanation, setExplanation] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!predictionId) return;
    setLoading(true);
    api.getExplanation(predictionId)
      .then(d => setExplanation(d.data))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [predictionId]);

  return { explanation, loading };
}

export function useExplanationHistory(symbol, page = 1) {
  const [explanations, setExplanations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [pagination, setPagination] = useState(null);

  const fetch = useCallback(async () => {
    if (!symbol) return;
    setLoading(true);
    try {
      const d = await api.getExplanationHistory(symbol, page);
      setExplanations(d.data || []);
      if (d.pagination) setPagination(d.pagination);
    } catch {}
    finally { setLoading(false); }
  }, [symbol, page]);

  useEffect(() => { fetch(); }, [fetch]);
  return { explanations, loading, pagination, refetch: fetch };
}

export function useAllExplanations(params = {}) {
  const [explanations, setExplanations] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Explanations are fetched per symbol; for /explanations page use prediction history
    api.getPredictions ? setLoading(false) : setLoading(false);
  }, []);

  return { explanations, loading };
}
