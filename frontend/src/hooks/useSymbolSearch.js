/**
 * File: frontend/src/hooks/useSymbolSearch.js
 * Symbol search hook with debounce + state management.
 *
 * SPEC Section 4.1 FR-001 — Global Symbol Search
 */
'use client';
import { useState, useEffect, useCallback, useRef } from 'react';
import api from '@/lib/api';
import { debounce } from '@/lib/utils';

export function useSymbolSearch() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const debouncedSearch = useRef(
    debounce(async (q) => {
      if (!q || q.length < 1) { setResults([]); setLoading(false); return; }
      setLoading(true);
      try {
        const d = await api.searchSymbols(q, 10);
        setResults(d.data?.results || d.data || []);
      } catch (e) {
        setError(e.message);
        setResults([]);
      } finally {
        setLoading(false);
      }
    }, 300)
  ).current;

  useEffect(() => {
    if (query.length === 0) { setResults([]); setLoading(false); return; }
    setLoading(true);
    debouncedSearch(query);
  }, [query, debouncedSearch]);

  const clear = useCallback(() => {
    setQuery('');
    setResults([]);
    setError(null);
  }, []);

  return { query, setQuery, results, loading, error, clear };
}

export function useSymbolDetail(ticker) {
  const [symbol, setSymbol] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!ticker) return;
    setLoading(true);
    api.getSymbol(ticker)
      .then(d => setSymbol(d.data))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [ticker]);

  return { symbol, loading };
}
