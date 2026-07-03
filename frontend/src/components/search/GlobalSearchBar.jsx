/**
 * File: frontend/src/components/search/GlobalSearchBar.jsx
 * Full-screen search overlay with autocomplete.
 *
 * SPEC Section 7.4 — Global Search Bar Design
 * SPEC Section 4.1 FR-001 — Global Symbol Search
 */
'use client';
import { useState, useEffect, useRef, useCallback } from 'react';
import { Search, X, ArrowRight, TrendingUp, BarChart2, Boxes, Globe } from 'lucide-react';
import { useSymbolSearch } from '@/hooks/useSymbolSearch';
import { useGeneratePrediction } from '@/hooks/usePredictions';
import SymbolDetailPanel from './SymbolDetailPanel';

const TYPE_ICONS = {
  stock: TrendingUp,
  etf: BarChart2,
  index: Globe,
  commodity: Boxes,
  futures: Boxes,
};

const TYPE_LABELS = {
  stock: 'Stocks',
  etf: 'ETFs',
  index: 'Indices',
  commodity: 'Commodities',
  futures: 'Futures',
};

function groupByType(results) {
  const groups = {};
  results.forEach(r => {
    const type = r.asset_type || r.type || 'stock';
    if (!groups[type]) groups[type] = [];
    groups[type].push(r);
  });
  return groups;
}

export default function GlobalSearchBar({ onClose }) {
  const inputRef = useRef(null);
  const { query, setQuery, results, loading } = useSymbolSearch();
  const { generate, generating } = useGeneratePrediction();
  const [selectedSymbol, setSelectedSymbol] = useState(null);
  const [selectedIndex, setSelectedIndex] = useState(-1);
  const flatResults = results;

  useEffect(() => {
    // Auto-focus
    setTimeout(() => inputRef.current?.focus(), 50);

    const handleKey = (e) => {
      if (e.key === 'Escape') {
        if (selectedSymbol) setSelectedSymbol(null);
        else onClose();
      }
    };
    document.addEventListener('keydown', handleKey);
    return () => document.removeEventListener('keydown', handleKey);
  }, [onClose, selectedSymbol]);

  const handleSelect = useCallback(async (symbol) => {
    setSelectedSymbol(symbol);
    try {
      await generate(symbol.ticker || symbol.symbol);
    } catch {}
  }, [generate]);

  const handleKeyDown = (e) => {
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setSelectedIndex(i => Math.min(i + 1, flatResults.length - 1));
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setSelectedIndex(i => Math.max(i - 1, 0));
    } else if (e.key === 'Enter' && selectedIndex >= 0 && flatResults[selectedIndex]) {
      handleSelect(flatResults[selectedIndex]);
    }
  };

  const groups = groupByType(results);

  if (selectedSymbol) {
    return (
      <SymbolDetailPanel
        symbol={selectedSymbol}
        generating={generating}
        onClose={() => {
          setSelectedSymbol(null);
          onClose();
        }}
        onBack={() => setSelectedSymbol(null)}
      />
    );
  }

  return (
    <div className="fixed inset-0 z-50 flex flex-col" style={{ background: 'rgba(0,0,0,0.75)' }}>
      <div
        className="w-full max-w-2xl mx-auto mt-16 rounded-2xl border shadow-2xl overflow-hidden"
        style={{ background: 'var(--bg-card)', borderColor: 'var(--border)' }}
      >
        {/* Search input */}
        <div className="flex items-center gap-3 px-4 py-3 border-b" style={{ borderColor: 'var(--border)' }}>
          <Search size={18} style={{ color: 'var(--text-muted)', flexShrink: 0 }} />
          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={e => { setQuery(e.target.value); setSelectedIndex(-1); }}
            onKeyDown={handleKeyDown}
            placeholder="Search any US stock, index, ETF, or commodity… (e.g. AAPL, Gold, SPY)"
            className="flex-1 bg-transparent outline-none text-base"
            style={{ color: 'var(--text-primary)' }}
          />
          {loading && (
            <div className="w-4 h-4 border-2 border-blue-400/50 border-t-blue-400 rounded-full animate-spin" />
          )}
          <button onClick={onClose} className="p-1 rounded hover:bg-white/10">
            <X size={16} style={{ color: 'var(--text-muted)' }} />
          </button>
        </div>

        {/* Results */}
        {results.length > 0 && (
          <div className="max-h-96 overflow-y-auto py-2">
            {Object.entries(groups).map(([type, items]) => (
              <div key={type}>
                <div className="px-4 py-1.5 text-xs font-semibold uppercase tracking-wider" style={{ color: 'var(--text-muted)' }}>
                  {TYPE_LABELS[type] || type}
                </div>
                {items.map((item, idx) => {
                  const globalIdx = flatResults.indexOf(item);
                  const Icon = TYPE_ICONS[type] || TrendingUp;
                  return (
                    <button
                      key={item.ticker || item.symbol}
                      className="flex items-center gap-3 w-full px-4 py-2.5 hover:bg-white/5 transition-colors text-left"
                      style={{ background: globalIdx === selectedIndex ? 'var(--bg-secondary)' : undefined }}
                      onClick={() => handleSelect(item)}
                    >
                      <div
                        className="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0"
                        style={{ background: 'var(--bg-secondary)' }}
                      >
                        <Icon size={15} style={{ color: '#2A7A6F' }} />
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2">
                          <span className="font-mono font-bold text-sm" style={{ color: 'var(--text-primary)' }}>
                            {item.ticker || item.symbol}
                          </span>
                          {item.exchange && (
                            <span className="text-xs px-1.5 py-0.5 rounded" style={{ background: 'var(--bg-secondary)', color: 'var(--text-muted)' }}>
                              {item.exchange}
                            </span>
                          )}
                        </div>
                        <div className="text-xs truncate" style={{ color: 'var(--text-muted)' }}>
                          {item.name}
                        </div>
                      </div>
                      <ArrowRight size={14} style={{ color: 'var(--text-muted)', flexShrink: 0 }} />
                    </button>
                  );
                })}
              </div>
            ))}
          </div>
        )}

        {/* Empty state */}
        {query.length > 0 && !loading && results.length === 0 && (
          <div className="py-10 text-center" style={{ color: 'var(--text-muted)' }}>
            <p className="text-sm">No results for &ldquo;{query}&rdquo;</p>
            <p className="text-xs mt-1">Try a ticker symbol (e.g. AAPL) or company name</p>
          </div>
        )}

        {/* Hint when empty */}
        {query.length === 0 && (
          <div className="px-4 py-8 text-center" style={{ color: 'var(--text-muted)' }}>
            <p className="text-sm mb-3">Popular symbols</p>
            <div className="flex flex-wrap gap-2 justify-center">
              {['SPY', 'AAPL', 'TSLA', 'NVDA', 'QQQ', 'GLD', 'CL=F', 'BTC-USD'].map(s => (
                <button
                  key={s}
                  className="px-3 py-1.5 rounded-lg text-xs font-mono font-medium border hover:bg-white/5 transition-colors"
                  style={{ borderColor: 'var(--border)', color: 'var(--text-secondary)' }}
                  onClick={() => setQuery(s)}
                >
                  {s}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Footer hint */}
        <div className="flex items-center justify-between px-4 py-2 border-t text-xs" style={{ borderColor: 'var(--border)', color: 'var(--text-muted)' }}>
          <span>↑↓ navigate</span>
          <span>↵ select</span>
          <span>Esc close</span>
        </div>
      </div>
    </div>
  );
}
