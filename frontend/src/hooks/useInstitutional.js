'use client';
import { useState, useEffect } from 'react';
import api from '@/lib/api';

export function useEtfFlows(symbol = 'SPY') {
  const [flows, setFlows] = useState(null);
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    api.getEtfFlows(symbol)
      .then(d => setFlows(d.data))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [symbol]);
  return { flows, loading };
}

export function useInsiderTransactions(symbol) {
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(false);
  useEffect(() => {
    if (!symbol) return;
    setLoading(true);
    api.getInsiderTransactions(symbol)
      .then(d => setTransactions(d.data || []))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [symbol]);
  return { transactions, loading };
}

export function use13fHoldings(symbol) {
  const [holdings, setHoldings] = useState([]);
  const [loading, setLoading] = useState(false);
  useEffect(() => {
    if (!symbol) return;
    setLoading(true);
    api.get13fHoldings(symbol)
      .then(d => setHoldings(d.data || []))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [symbol]);
  return { holdings, loading };
}

export function useDarkPool(symbol) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  useEffect(() => {
    if (!symbol) return;
    setLoading(true);
    api.getDarkPool(symbol)
      .then(d => setData(d.data))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [symbol]);
  return { data, loading };
}
