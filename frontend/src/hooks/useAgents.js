/**
 * File: frontend/src/hooks/useAgents.js
 * Hooks for agent definitions, outputs, and triggering runs.
 *
 * SPEC Section 16.1 — Agents endpoints
 */
'use client';
import { useState, useEffect, useCallback, useMemo } from 'react';
import api from '@/lib/api';

export function useAgentDefinitions() {
  const [agents, setAgents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetch = useCallback(async () => {
    setLoading(true);
    try {
      const d = await api.listAgents();
      setAgents(d.data || []);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetch(); }, [fetch]);
  return { agents, loading, error, refetch: fetch };
}

export function useAgentResults(symbol) {
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetch = useCallback(async () => {
    if (!symbol) return;
    setLoading(true); setError(null);
    try {
      const d = await api.getAgentResults(symbol);
      // Backend returns { data: { agents: [...] } } or { data: [...] }
      const raw = d.data;
      setResults(Array.isArray(raw) ? raw : raw?.agents || []);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, [symbol]);

  useEffect(() => { fetch(); }, [fetch]);
  return { results, loading, error, refetch: fetch };
}

export function useRunAgents(symbol) {
  const [running, setRunning] = useState(false);
  const [error, setError] = useState(null);

  const run = useCallback(async () => {
    if (!symbol) return;
    setRunning(true); setError(null);
    try {
      await api.runAgents(symbol);
    } catch (e) {
      setError(e.message);
    } finally {
      setRunning(false);
    }
  }, [symbol]);

  return { run, running, error };
}

export function useTriggerAgent() {
  const [triggering, setTriggering] = useState(false);
  const [error, setError] = useState(null);

  const trigger = useCallback(async (agentId, symbol) => {
    setTriggering(true); setError(null);
    try {
      const d = await api.triggerAgent(agentId, symbol);
      return d.data;
    } catch (e) {
      setError(e.message);
      throw e;
    } finally {
      setTriggering(false);
    }
  }, []);

  return { trigger, triggering, error };
}

/** Group agent results by category bucket */
export function useAgentsByCategory(results = []) {
  return useMemo(() => {
    const groups = {};
    results.forEach(r => {
      const id = r.agent_id;
      let cat = 'Other';
      if (id <= 6)        cat = 'Direction';
      else if (id <= 14)  cat = 'News & Macro';
      else if (id <= 20)  cat = 'Institutional';
      else if (id <= 26)  cat = 'Strength';
      else if (id <= 29)  cat = 'Exit & Reversal';
      else if (id <= 33)  cat = 'Prediction Layer';
      else if (id === 34) cat = 'Additional';
      else                cat = 'Commodity';
      if (!groups[cat]) groups[cat] = [];
      groups[cat].push(r);
    });
    return groups;
  }, [results]);
}
