/**
 * File: frontend/src/lib/utils.js
 * Shared utility functions — formatters, helpers, class merging.
 */
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs) {
  return twMerge(clsx(inputs));
}

export function formatCurrency(value, decimals = 2) {
  if (value === null || value === undefined || isNaN(value)) return '—';
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(value);
}

export function formatNumber(value, decimals = 2) {
  if (value === null || value === undefined || isNaN(value)) return '—';
  return new Intl.NumberFormat('en-US', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(value);
}

export function formatPct(value, decimals = 1) {
  if (value === null || value === undefined || isNaN(value)) return '—';
  const sign = value >= 0 ? '+' : '';
  return `${sign}${Number(value).toFixed(decimals)}%`;
}

export function formatLargeNumber(value) {
  if (value === null || value === undefined || isNaN(value)) return '—';
  const abs = Math.abs(value);
  if (abs >= 1e12) return `$${(value / 1e12).toFixed(2)}T`;
  if (abs >= 1e9) return `$${(value / 1e9).toFixed(2)}B`;
  if (abs >= 1e6) return `$${(value / 1e6).toFixed(2)}M`;
  if (abs >= 1e3) return `$${(value / 1e3).toFixed(1)}K`;
  return `$${value}`;
}

export function formatRelativeTime(dateStr) {
  if (!dateStr) return '—';
  const date = new Date(dateStr);
  const now = new Date();
  const diff = now - date;
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return 'Just now';
  if (mins < 60) return `${mins}m ago`;
  const hours = Math.floor(mins / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  if (days < 7) return `${days}d ago`;
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}

export function formatDate(dateStr, opts = {}) {
  if (!dateStr) return '—';
  const date = new Date(dateStr);
  return date.toLocaleDateString('en-US', {
    year: 'numeric', month: 'short', day: 'numeric',
    ...opts,
  });
}

export function signalColor(signal) {
  switch (signal) {
    case 'Bullish': return 'text-green-400';
    case 'Bearish': return 'text-red-400';
    default: return 'text-yellow-400';
  }
}

export function signalBg(signal) {
  switch (signal) {
    case 'Bullish': return 'bg-green-500/10 text-green-400 border border-green-500/20';
    case 'Bearish': return 'bg-red-500/10 text-red-400 border border-red-500/20';
    default: return 'bg-yellow-500/10 text-yellow-400 border border-yellow-500/20';
  }
}

export function confidenceColor(confidence) {
  if (confidence >= 75) return 'text-green-400';
  if (confidence >= 55) return 'text-yellow-400';
  return 'text-red-400';
}

export function riskColor(risk) {
  if (risk <= 35) return 'text-green-400';
  if (risk <= 65) return 'text-yellow-400';
  return 'text-red-400';
}

export function debounce(fn, ms = 300) {
  let timer;
  return (...args) => {
    clearTimeout(timer);
    timer = setTimeout(() => fn(...args), ms);
  };
}

export function clamp(val, min, max) {
  return Math.min(Math.max(val, min), max);
}
