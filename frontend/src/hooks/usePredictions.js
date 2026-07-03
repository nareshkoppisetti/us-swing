/**
 * File: frontend/src/hooks/usePredictions.js
 * Hooks for predictions — fetch, generate, history, watchlist.
 *
 * SPEC Section 16.1 — Predictions endpoints
 */
'use client';
import { useState, useEffect, useCallback } from 'react';
import api from '@/lib/api';

export function usePrediction(symbol) {
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetch = useCallback(async () => {
    if (!symbol) return;
    setLoading(true); setError(null);
    try {
      const d = await api.getPrediction(symbol);
      setPrediction(d.data);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, [symbol]);

  useEffect(() => { fetch(); }, [fetch]);
  return { prediction, loading, error, refetch: fetch };
}

export function useGeneratePrediction() {
  const [generating, setGenerating] = useState(false);
  const [prediction, setPrediction] = useState(null);
  const [error, setError] = useState(null);

  const generate = useCallback(async (symbol) => {
    setGenerating(true); setError(null);
    try {
      const d = await api.generatePrediction(symbol);
      setPrediction(d.data);
      return d.data;
    } catch (e) {
      setError(e.message);
      throw e;
    } finally {
      setGenerating(false);
    }
  }, []);

  return { generate, generating, prediction, error };
}

export function usePredictionHistory(symbol, limit = 20) {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!symbol) return;
    setLoading(true);
    api.getPredictionHistory(symbol, limit)
      .then(d => setHistory(d.data?.history || d.data || []))
      .catch(e => setError(e.message))
      .finally(() => setLoading(false));
  }, [symbol, limit]);

  return { history, loading, error };
}

export function usePredictions(params = {}) {
  const [predictions, setPredictions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [pagination, setPagination] = useState(null);

  const fetch = useCallback(async () => {
    setLoading(true); setError(null);
    try {
      const d = await api.getPredictions(params);
      setPredictions(d.data || []);
      if (d.pagination) setPagination(d.pagination);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, [JSON.stringify(params)]);

  useEffect(() => { fetch(); }, [fetch]);
  return { predictions, loading, error, pagination, refetch: fetch };
}

export function useWatchlistSignals() {
  const [signals, setSignals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetch = useCallback(async () => {
    setLoading(true); setError(null);
    try {
      const d = await api.getWatchlistSignals();
      setSignals(d.data || []);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetch(); }, [fetch]);
  return { signals, loading, error, refetch: fetch };
}

export function useSymbolPredictions(symbol) {
  const [predictions, setPredictions] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!symbol) return;
    setLoading(true);
    api.getSymbolPredictions(symbol)
      .then(d => setPredictions(d.data || []))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [symbol]);

  return { predictions, loading };
}
