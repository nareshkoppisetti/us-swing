'use client';
import { useState, useEffect } from 'react';
import api from '@/lib/api';

export function useHistory(params = {}) {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [pagination, setPagination] = useState(null);

  useEffect(() => {
    api.getPredictions({ ...params, status: 'resolved' })
      .then(d => {
        setHistory(d.data || []);
        if (d.pagination) setPagination(d.pagination);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [JSON.stringify(params)]);

  return { history, loading, pagination };
}
