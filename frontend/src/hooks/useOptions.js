'use client';
import { useState, useEffect } from 'react';
import api from '@/lib/api';

export function useOptionsChain(symbol) {
  const [chain, setChain] = useState(null);
  const [loading, setLoading] = useState(false);
  useEffect(() => {
    if (!symbol) return;
    setLoading(true);
    api.getOptionsChain(symbol)
      .then(d => setChain(d.data))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [symbol]);
  return { chain, loading };
}

export function useGEX(symbol) {
  const [gex, setGex] = useState(null);
  const [loading, setLoading] = useState(false);
  useEffect(() => {
    if (!symbol) return;
    setLoading(true);
    api.getGEX(symbol)
      .then(d => setGex(d.data))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [symbol]);
  return { gex, loading };
}

export function useOIStructure(symbol) {
  const [oi, setOi] = useState(null);
  const [loading, setLoading] = useState(false);
  useEffect(() => {
    if (!symbol) return;
    setLoading(true);
    // No standalone "OI structure" endpoint in the API spec — the options
    // chain itself carries open_interest per strike, which is what this
    // hook actually needs.
    api.getOptionsChain(symbol)
      .then(d => setOi(d.data))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [symbol]);
  return { oi, loading };
}

export function usePutCallRatio(symbol) {
  const [ratio, setRatio] = useState(null);
  const [loading, setLoading] = useState(false);
  useEffect(() => {
    if (!symbol) return;
    setLoading(true);
    api.getPutCallRatio(symbol)
      .then(d => setRatio(d.data))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [symbol]);
  return { ratio, loading };
}
