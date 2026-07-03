/**
 * File: frontend/src/components/search/SearchAutocomplete.jsx
 * Reusable inline autocomplete dropdown for symbol search.
 */
'use client';
import { TrendingUp, BarChart2, Globe, Boxes } from 'lucide-react';

const TYPE_ICONS = { stock: TrendingUp, etf: BarChart2, index: Globe, commodity: Boxes, futures: Boxes };

export default function SearchAutocomplete({ results = [], loading = false, onSelect, onClose }) {
  if (loading) {
    return (
      <div className="rounded-xl border p-4" style={{ background: 'var(--bg-card)', borderColor: 'var(--border)' }}>
        <div className="flex items-center gap-2 text-sm" style={{ color: 'var(--text-muted)' }}>
          <div className="w-4 h-4 border-2 border-blue-400/40 border-t-blue-400 rounded-full animate-spin" />
          Searching…
        </div>
      </div>
    );
  }

  if (!results || results.length === 0) {
    return (
      <div className="rounded-xl border p-4 text-sm" style={{ background: 'var(--bg-card)', borderColor: 'var(--border)', color: 'var(--text-muted)' }}>
        No matches found
      </div>
    );
  }

  return (
    <div className="rounded-xl border overflow-hidden shadow-xl" style={{ background: 'var(--bg-card)', borderColor: 'var(--border)' }}>
      {results.map((item) => {
        const Icon = TYPE_ICONS[item.asset_type || item.type] || TrendingUp;
        return (
          <button
            key={item.ticker || item.symbol}
            className="flex items-center gap-3 w-full px-4 py-2.5 hover:bg-white/5 transition-colors text-left"
            onClick={() => { onSelect?.(item); onClose?.(); }}
          >
            <div className="w-7 h-7 rounded-lg flex items-center justify-center flex-shrink-0" style={{ background: 'var(--bg-secondary)' }}>
              <Icon size={13} style={{ color: '#2A7A6F' }} />
            </div>
            <div className="flex-1 min-w-0">
              <span className="font-mono font-bold text-sm mr-2" style={{ color: 'var(--text-primary)' }}>
                {item.ticker || item.symbol}
              </span>
              <span className="text-xs truncate" style={{ color: 'var(--text-muted)' }}>{item.name}</span>
            </div>
            {item.exchange && (
              <span className="text-xs px-1.5 py-0.5 rounded flex-shrink-0" style={{ background: 'var(--bg-secondary)', color: 'var(--text-muted)' }}>
                {item.exchange}
              </span>
            )}
          </button>
        );
      })}
    </div>
  );
}
