/**
 * File: frontend/src/hooks/useMarketData.js
 * Hooks for OHLCV, quotes, indicators, market regime, and VIX.
 *
 * SPEC Section 16.1 — Market Data endpoints
 */
'use client';
import { useState, useEffect, useCallback, useRef } from 'react';
import api from '@/lib/api';
import { useWebSocket } from '@/hooks/useWebSocket';

// Fallback poll interval used only while the websocket is disconnected.
// 2s is fast enough to feel live without hammering the quote endpoint hard
// enough to trigger the partial/empty responses that caused the flicker.
const QUOTE_FALLBACK_POLL_MS = 2000;

export function useOHLCV(symbol, { timeframe = 'daily', period = '1y' } = {}) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!symbol) return;
    setLoading(true); setError(null);
    api.getOHLCV(symbol, { timeframe, period })
      .then(d => setData(d.data))
      .catch(e => setError(e.message))
      .finally(() => setLoading(false));
  }, [symbol, timeframe, period]);

  return { data, loading, error };
}

export function useQuote(symbol) {
  const [quote, setQuote] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const { subscribe } = useWebSocket();
  const intervalRef = useRef(null);

  // `background: true` skips the loading flag so periodic refreshes update
  // the numbers in place without the UI blinking/collapsing every second.
  const fetch = useCallback(async ({ background = false } = {}) => {
    if (!symbol) return;
    if (!background) { setLoading(true); setError(null); }
    try {
      const d = await api.getQuote(symbol);
      const next = d?.data;
      // A poll that comes back with no price (rate-limited, mid-refresh on
      // the backend, transient hiccup, etc.) must NOT erase what's already
      // on screen — that's what was causing the price row to disappear and
      // reappear ("blinking"). Merge on top of the last good quote instead
      // of replacing it outright, and only if there's real data to merge.
      if (next && next.price != null) {
        setQuote(prev => ({ ...prev, ...next }));
      } else if (!background && next) {
        // First load, even if incomplete — still show whatever came back.
        setQuote(next);
      }
      if (background) setError(null);
    } catch (e) {
      // Keep showing the last good quote; just record the error.
      setError(e.message);
    } finally {
      if (!background) setLoading(false);
    }
  }, [symbol]);

  // Real loading state: only on first mount / when the symbol changes.
  useEffect(() => {
    setQuote(null);
    fetch();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [symbol]);

  // Instant live updates: apply ticks for this symbol the moment they arrive.
  useEffect(() => {
    if (!symbol) return;
    const unsub = subscribe('market_data', (data) => {
      if (data?.symbol === symbol) setQuote(q => ({ ...q, ...data }));
    });
    return unsub;
  }, [symbol, subscribe]);

  // Fast background polling (backend has no live push feed for quotes yet —
  // see note at the top of this file). The websocket listener above still
  // upgrades this to instant push automatically once that feed exists.
  // Runs silently — never re-triggers the loading state.
  useEffect(() => {
    if (!symbol) return;
    clearInterval(intervalRef.current);
    intervalRef.current = setInterval(() => fetch({ background: true }), QUOTE_FALLBACK_POLL_MS);
    return () => clearInterval(intervalRef.current);
  }, [symbol, fetch]);

  return { quote, loading, error, refetch: fetch };
}

export function useMarketRegime() {
  const [regime, setRegime] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetch = useCallback(async () => {
    setLoading(true); setError(null);
    try {
      const d = await api.getMarketRegime();
      setRegime(d.data);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetch(); }, [fetch]);
  return { regime, loading, error, refetch: fetch };
}

export function useVIX() {
  const [vix, setVix] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    api.getVIX()
      .then(d => setVix(d.data))
      .catch(e => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  return { vix, loading, error };
}

export function useIndicators(symbol) {
  const [indicators, setIndicators] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!symbol) return;
    setLoading(true);
    api.getIndicators(symbol)
      .then(d => setIndicators(d.data))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [symbol]);

  return { indicators, loading };
}
