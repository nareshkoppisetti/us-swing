'use client';
import { useEffect } from 'react';

export function useAutoRefresh(callback, intervalMs = 30000) {
  useEffect(() => {
    const id = setInterval(callback, intervalMs);
    return () => clearInterval(id);
  }, [callback, intervalMs]);
}
