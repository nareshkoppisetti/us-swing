'use client';
/**
 * File: frontend/src/app/signals/page.jsx
 * Signals page — watchlist + search for individual symbol signals.
 */
import { useState } from 'react';
import Link from 'next/link';
import { useWatchlistSignals } from '@/hooks/usePredictions';
import { useSymbolSearch } from '@/hooks/useSymbolSearch';
import api from '@/lib/api';

const SIG = { Bullish:'text-green-400 bg-green-400/10 border-green-400/30',
              Bearish:'text-red-400 bg-red-400/10 border-red-400/30',
              Neutral:'text-yellow-400 bg-yellow-400/10 border-yellow-400/30' };

function SignalCard({ item }) {
  const cls = SIG[item.signal] || SIG.Neutral;
  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-4 hover:border-gray-600 transition-colors">
      <div className="flex items-center justify-between mb-3">
        <Link href={`/predictions?symbol=${item.symbol}`} className="font-mono text-blue-400 font-bold text-lg hover:text-blue-300">
          {item.symbol}
        </Link>
        <span className={`text-sm px-2.5 py-1 rounded-lg border font-semibold ${cls}`}>{item.signal}</span>
      </div>
      <div className="grid grid-cols-2 gap-2 text-xs text-gray-400">
        <div>Score <span className="text-gray-200 font-semibold">{item.score?.toFixed(1)}</span></div>
        <div>Conf <span className="text-gray-200 font-semibold">{item.confidence?.toFixed(0)}%</span></div>
        <div>5d <span className={`font-semibold ${item['5d_direction'] === 'Bullish' ? 'text-green-400' : item['5d_direction'] === 'Bearish' ? 'text-red-400' : 'text-yellow-400'}`}>{item['5d_direction'] || 'Neutral'}</span></div>
        <div>20d <span className={`font-semibold ${item['20d_direction'] === 'Bullish' ? 'text-green-400' : item['20d_direction'] === 'Bearish' ? 'text-red-400' : 'text-yellow-400'}`}>{item['20d_direction'] || 'Neutral'}</span></div>
      </div>
      {item.generated_at && (
        <div className="mt-2 text-xs text-gray-600">{new Date(item.generated_at).toLocaleString()}</div>
      )}
    </div>
  );
}

export default function SignalsPage() {
  const { signals, loading, refetch } = useWatchlistSignals();
  const { query, setQuery, results } = useSymbolSearch();
  const [searchSignal, setSearchSignal] = useState(null);
  const [searching, setSearching] = useState(false);

  const fetchSignal = async (ticker) => {
    setSearching(true);
    try {
      const d = await api.getSignal(ticker);
      setSearchSignal(d.data);
    } catch { setSearchSignal(null); }
    finally { setSearching(false); }
  };

  return (
    <div className="min-h-screen bg-gray-950 text-gray-100 p-6">
      <div className="max-w-6xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold text-white">Signals</h1>
            <p className="text-gray-400 text-sm mt-0.5">Trade signals from the 42-agent pipeline</p>
          </div>
          <button onClick={refetch} className="text-sm text-blue-400 hover:text-blue-300 border border-blue-400/30 px-3 py-1.5 rounded-lg transition-colors">
            Refresh
          </button>
        </div>

        {/* Search */}
        <div className="relative mb-6">
          <input
            className="w-full bg-gray-800 border border-gray-700 rounded-xl px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-blue-500 text-sm uppercase"
            placeholder="Search for any symbol…"
            value={query}
            onChange={e => setQuery(e.target.value)}
          />
          {results.length > 0 && (
            <div className="absolute z-10 w-full mt-1 bg-gray-800 border border-gray-700 rounded-xl overflow-hidden shadow-2xl">
              {results.slice(0,5).map(r => (
                <button key={r.ticker} onClick={() => fetchSignal(r.ticker)}
                  className="w-full flex items-center gap-3 px-4 py-2.5 hover:bg-gray-700 text-left">
                  <span className="font-mono text-blue-400 text-sm font-semibold w-14">{r.ticker}</span>
                  <span className="text-gray-300 text-sm truncate">{r.name}</span>
                </button>
              ))}
            </div>
          )}
        </div>

        {searchSignal && (
          <div className="mb-6">
            <div className="text-xs text-gray-500 uppercase tracking-wider mb-2">Search Result</div>
            <SignalCard item={searchSignal} />
          </div>
        )}

        {/* Watchlist grid */}
        <div className="text-xs text-gray-500 uppercase tracking-wider mb-3">Watchlist</div>
        {loading ? (
          <div className="text-gray-600 animate-pulse text-sm">Loading signals…</div>
        ) : signals.length > 0 ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {signals.map(s => <SignalCard key={s.symbol} item={s} />)}
          </div>
        ) : (
          <div className="text-center py-12 text-gray-500 text-sm">
            No signals yet. Run agents for watchlist symbols via the <Link href="/agents" className="text-blue-400 hover:underline">Agents</Link> page.
          </div>
        )}
      </div>
    </div>
  );
}
