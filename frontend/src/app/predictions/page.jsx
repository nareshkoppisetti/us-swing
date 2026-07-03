'use client';
/**
 * File: frontend/src/app/predictions/page.jsx
 * Prediction dashboard — final Agent 33 output with per-horizon breakdown.
 */
import { useState } from 'react';
import { usePrediction, useGeneratePrediction, usePredictionHistory } from '@/hooks/usePredictions';
import { useSymbolSearch } from '@/hooks/useSymbolSearch';
import MainLayout from '@/components/layout/MainLayout';

const SIGNAL_STYLE = {
  Bullish: { bg: 'bg-green-500/10', border: 'border-green-500/40', text: 'text-green-400', dot: 'bg-green-400' },
  Bearish: { bg: 'bg-red-500/10',   border: 'border-red-500/40',   text: 'text-red-400',   dot: 'bg-red-400'   },
  Neutral: { bg: 'bg-yellow-500/10',border: 'border-yellow-500/40',text: 'text-yellow-400',dot: 'bg-yellow-400' },
};
const RISK_COLOR = { Low: 'text-green-400', Moderate: 'text-yellow-400', High: 'text-red-400' };

function ScoreMeter({ score, signal }) {
  const s = SIGNAL_STYLE[signal] || SIGNAL_STYLE.Neutral;
  return (
    <div className="relative">
      <div className="flex justify-between text-xs text-gray-500 mb-1">
        <span>Bearish 0</span><span>Neutral 50</span><span>100 Bullish</span>
      </div>
      <div className="h-3 bg-gray-800 rounded-full overflow-hidden">
        <div
          className={`h-full rounded-full transition-all duration-700 ${s.dot === 'bg-green-400' ? 'bg-gradient-to-r from-green-600 to-green-400' : s.dot === 'bg-red-400' ? 'bg-gradient-to-r from-red-600 to-red-400' : 'bg-gradient-to-r from-yellow-600 to-yellow-400'}`}
          style={{ width: `${Math.max(2, Math.min(100, score))}%` }}
        />
      </div>
      <div className="absolute top-5 font-bold text-lg" style={{ left: `${Math.max(2, Math.min(97, score))}%`, transform: 'translateX(-50%)' }}>
        <span className={s.text}>{score?.toFixed(1)}</span>
      </div>
    </div>
  );
}

function HorizonRow({ p }) {
  const s = SIGNAL_STYLE[p.direction] || SIGNAL_STYLE.Neutral;
  return (
    <div className={`flex items-center justify-between p-3 rounded-lg border ${s.bg} ${s.border}`}>
      <span className="text-gray-300 text-sm font-medium">{p.horizon_days}d horizon</span>
      <div className="flex items-center gap-3">
        <div className="w-24">
          <div className="h-1.5 bg-gray-800 rounded-full overflow-hidden">
            <div className={`h-full rounded-full ${s.dot}`} style={{ width: `${p.score}%` }} />
          </div>
        </div>
        <span className={`text-sm font-semibold ${s.text} w-16 text-right`}>{p.direction}</span>
        <span className="text-xs text-gray-400 w-12 text-right">
          {p.expected_return_pct > 0 ? '+' : ''}{p.expected_return_pct?.toFixed(1)}%
        </span>
        <span className="text-xs text-gray-500 w-14 text-right">{p.confidence?.toFixed(0)}% conf</span>
      </div>
    </div>
  );
}

export default function PredictionsPage() {
  const [symbol, setSymbol] = useState('');
  const [activeSymbol, setActiveSymbol] = useState('');
  const { query, setQuery, results: searchResults } = useSymbolSearch();
  const [showSearch, setShowSearch] = useState(false);

  const { prediction, loading, error, refetch } = usePrediction(activeSymbol);
  const { generate, generating } = useGeneratePrediction();
  const { history } = usePredictionHistory(activeSymbol);

  const handleSelect = (ticker) => {
    setActiveSymbol(ticker);
    setSymbol(ticker);
    setQuery('');
    setShowSearch(false);
  };

  const handleGenerate = async () => {
    await generate(activeSymbol);
    refetch();
  };

  const pred = prediction;
  const signal = pred?.signal || 'Neutral';
  const s = SIGNAL_STYLE[signal] || SIGNAL_STYLE.Neutral;

  return (
    <MainLayout>
    <div className="min-h-screen bg-gray-950 text-gray-100 p-6">
      <div className="max-w-4xl mx-auto">
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-white">Predictions</h1>
          <p className="text-gray-400 text-sm mt-0.5">42-agent composite prediction engine</p>
        </div>

        {/* Symbol selector */}
        <div className="relative mb-6">
          <input
            className="w-full bg-gray-800 border border-gray-700 rounded-xl px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-blue-500 text-sm uppercase"
            placeholder="Enter symbol (e.g. AAPL, SPY, TSLA)…"
            value={query || symbol}
            onChange={e => { setQuery(e.target.value); setShowSearch(true); }}
            onFocus={() => setShowSearch(true)}
          />
          {showSearch && searchResults.length > 0 && (
            <div className="absolute z-10 w-full mt-1 bg-gray-800 border border-gray-700 rounded-xl shadow-2xl overflow-hidden">
              {searchResults.map(r => (
                <button
                  key={r.ticker}
                  onClick={() => handleSelect(r.ticker)}
                  className="w-full flex items-center gap-3 px-4 py-2.5 hover:bg-gray-700 text-left transition-colors"
                >
                  <span className="font-mono text-blue-400 text-sm font-semibold w-16">{r.ticker}</span>
                  <span className="text-gray-300 text-sm truncate">{r.name}</span>
                  <span className="text-gray-500 text-xs ml-auto shrink-0">{r.symbol_type}</span>
                </button>
              ))}
            </div>
          )}
        </div>

        {activeSymbol && (
          <div className="flex items-center gap-3 mb-6">
            <span className="text-gray-300 font-semibold">{activeSymbol}</span>
            <button
              onClick={handleGenerate}
              disabled={generating || loading}
              className="bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white px-4 py-1.5 rounded-lg text-sm font-medium transition-colors"
            >
              {generating ? '⟳ Generating…' : '▶ Generate Prediction'}
            </button>
            {pred && (
              <span className="text-xs text-gray-500">
                Last: {pred.generated_at ? new Date(pred.generated_at).toLocaleString() : 'Unknown'}
              </span>
            )}
          </div>
        )}

        {error && !loading && (
          <div className="p-4 bg-gray-900 border border-gray-700 rounded-xl text-center text-gray-400 mb-6">
            No prediction yet. Click <strong>Generate Prediction</strong> to run the 42-agent pipeline.
          </div>
        )}

        {loading && (
          <div className="text-center py-12 text-gray-500">Loading prediction…</div>
        )}

        {pred && !loading && (
          <>
            {/* Main signal card */}
            <div className={`p-6 rounded-2xl border mb-4 ${s.bg} ${s.border}`}>
              <div className="flex items-start justify-between mb-4">
                <div>
                  <div className={`text-4xl font-black ${s.text}`}>{signal}</div>
                  <div className="text-gray-400 text-sm mt-1">
                    Risk: <span className={RISK_COLOR[pred.risk_level] || 'text-gray-300'}>{pred.risk_level}</span>
                    {pred.is_degraded && <span className="ml-2 text-orange-400 text-xs">[DEGRADED]</span>}
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-3xl font-bold text-white">{pred.confidence?.toFixed(1)}%</div>
                  <div className="text-gray-400 text-sm">Confidence</div>
                </div>
              </div>
              <div className="mb-8">
                <ScoreMeter score={pred.score} signal={signal} />
              </div>
            </div>

            {/* Per-horizon predictions */}
            {pred.predictions?.length > 0 && (
              <div className="bg-gray-900 border border-gray-800 rounded-2xl p-5 mb-4">
                <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-3">Horizon Predictions</h2>
                <div className="space-y-2">
                  {pred.predictions.map(p => <HorizonRow key={p.horizon_days} p={p} />)}
                </div>
              </div>
            )}

            {/* Factors */}
            <div className="grid grid-cols-2 gap-4 mb-4">
              {pred.bullish_factors?.length > 0 && (
                <div className="bg-green-500/5 border border-green-500/20 rounded-xl p-4">
                  <h3 className="text-green-400 text-xs font-semibold uppercase tracking-wider mb-2">Bullish Factors</h3>
                  <ul className="space-y-1">
                    {pred.bullish_factors.map((f, i) => (
                      <li key={i} className="text-gray-300 text-xs flex gap-1.5"><span className="text-green-500 shrink-0">+</span>{f}</li>
                    ))}
                  </ul>
                </div>
              )}
              {pred.bearish_factors?.length > 0 && (
                <div className="bg-red-500/5 border border-red-500/20 rounded-xl p-4">
                  <h3 className="text-red-400 text-xs font-semibold uppercase tracking-wider mb-2">Bearish Factors</h3>
                  <ul className="space-y-1">
                    {pred.bearish_factors.map((f, i) => (
                      <li key={i} className="text-gray-300 text-xs flex gap-1.5"><span className="text-red-500 shrink-0">−</span>{f}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>

            {/* Reasoning */}
            {pred.reasoning && (
              <div className="bg-gray-900 border border-gray-800 rounded-xl p-4 text-xs text-gray-400 leading-relaxed">
                {pred.reasoning}
              </div>
            )}
          </>
        )}

        {/* History chart (simple table) */}
        {history?.length > 1 && (
          <div className="mt-6 bg-gray-900 border border-gray-800 rounded-2xl p-5">
            <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-3">Signal History</h2>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-gray-500 text-xs border-b border-gray-800">
                    <th className="text-left pb-2">Date</th>
                    <th className="text-left pb-2">Signal</th>
                    <th className="text-right pb-2">Score</th>
                    <th className="text-right pb-2">Confidence</th>
                    <th className="text-right pb-2">Risk</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-800/50">
                  {history.slice(0, 10).map((h, i) => {
                    const hs = SIGNAL_STYLE[h.signal] || SIGNAL_STYLE.Neutral;
                    return (
                      <tr key={i} className="text-gray-300 text-xs">
                        <td className="py-2 text-gray-500">{h.generated_at ? new Date(h.generated_at).toLocaleDateString() : '—'}</td>
                        <td className={`py-2 font-semibold ${hs.text}`}>{h.signal}</td>
                        <td className="py-2 text-right">{h.score?.toFixed(1)}</td>
                        <td className="py-2 text-right">{h.confidence?.toFixed(1)}%</td>
                        <td className={`py-2 text-right ${RISK_COLOR[h.risk_level] || ''}`}>{h.risk_level || '—'}</td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
    </MainLayout>
  );
}
