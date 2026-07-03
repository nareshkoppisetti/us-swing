'use client';
import { useState, useEffect } from 'react';
import api from '@/lib/api';

export function useAccuracy(params = {}) {
  const [accuracy, setAccuracy] = useState(null);
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    api.getAccuracy(params)
      .then(d => setAccuracy(d.data))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [JSON.stringify(params)]);
  return { accuracy, loading };
}

export function useAgentPerformance() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    api.getAgentPerformance()
      .then(d => setData(d.data || []))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);
  return { data, loading };
}
