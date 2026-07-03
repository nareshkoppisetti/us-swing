'use client';
/**
 * File: frontend/src/app/history/page.jsx
 * Historical predictions with outcome tracking.
 */
import { useState, useEffect, useCallback } from 'react';
import MainLayout from '@/components/layout/MainLayout';
import { api } from '@/lib/api';
import { Activity, RefreshCw, CheckCircle, XCircle, Clock } from 'lucide-react';

const DIR_STYLE = {
  Bullish: 'text-green-400 bg-green-400/10 border-green-400/30',
  Bearish: 'text-red-400 bg-red-400/10 border-red-400/30',
  Neutral: 'text-yellow-400 bg-yellow-400/10 border-yellow-400/30',
};
const HORIZON_LABELS = { 2:'2D', 5:'5D', 10:'10D', 20:'20D', 30:'30D', 60:'60D' };

function PredictionRow({ pred }) {
  const dir = pred.direction || pred.signal;
  const outcome = pred.outcome;
  const correct = outcome === 'correct' || outcome === true;
  const incorrect = outcome === 'incorrect' || outcome === false;
  return (
    <tr className="border-b last:border-0 hover:bg-white/5 transition-colors"
      style={{ borderColor: 'var(--border)' }}>
      <td className="px-4 py-3 font-mono font-bold text-sm" style={{ color: '#2A7A6F' }}>{pred.symbol}</td>
      <td className="px-4 py-3 text-xs" style={{ color: 'var(--text-muted)' }}>
        {HORIZON_LABELS[pred.horizon_days] || `${pred.horizon_days}D`}
      </td>
      <td className="px-4 py-3">
        <span className={`text-xs px-2 py-0.5 rounded-full border font-semibold ${DIR_STYLE[dir] || DIR_STYLE.Neutral}`}>
          {dir || '—'}
        </span>
      </td>
      <td className="px-4 py-3 text-sm font-bold" style={{ color: 'var(--text-primary)' }}>
        {pred.confidence?.toFixed(0) ?? '—'}%
      </td>
      <td className="px-4 py-3 text-sm" style={{ color: pred.expected_move_pct >= 0 ? '#22c55e' : '#ef4444' }}>
        {pred.expected_move_pct != null ? `${pred.expected_move_pct >= 0 ? '+' : ''}${pred.expected_move_pct.toFixed(2)}%` : '—'}
      </td>
      <td className="px-4 py-3">
        {correct ? <CheckCircle size={15} className="text-green-400" />
          : incorrect ? <XCircle size={15} className="text-red-400" />
          : <Clock size={15} style={{ color: 'var(--text-muted)' }} />}
      </td>
      <td className="px-4 py-3 text-xs" style={{ color: 'var(--text-muted)' }}>
        {pred.created_at ? new Date(pred.created_at).toLocaleDateString() : '—'}
      </td>
    </tr>
  );
}

const SYMBOL_OPTS = ['ALL', 'SPY', 'QQQ', 'AAPL', 'TSLA', 'NVDA', 'GLD'];
const HORIZON_OPTS = [{ label: 'All', value: '' }, { label: '2D', value: 2 }, { label: '5D', value: 5 }, { label: '10D', value: 10 }, { label: '20D', value: 20 }, { label: '30D', value: 30 }, { label: '60D', value: 60 }];

export default function HistoryPage() {
  const [predictions, setPredictions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [symbol, setSymbol] = useState('ALL');
  const [horizon, setHorizon] = useState('');
  const [page, setPage] = useState(1);
  const [pagination, setPagination] = useState(null);

  const load = useCallback(async () => {
    setLoading(true); setError(null);
    try {
      const params = { page, page_size: 30 };
      if (symbol !== 'ALL') params.symbol = symbol;
      if (horizon) params.horizon = horizon;
      const res = await api.getPredictions(params);
      setPredictions(res.data || []);
      if (res.pagination) setPagination(res.pagination);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, [symbol, horizon, page]);

  useEffect(() => { load(); }, [load]);

  const total = predictions.length;
  const withOutcome = predictions.filter(p => p.outcome != null);
  const correct = withOutcome.filter(p => p.outcome === 'correct' || p.outcome === true).length;
  const winRate = withOutcome.length > 0 ? ((correct / withOutcome.length) * 100).toFixed(1) : null;

  return (
    <MainLayout>
      <div className="p-4 md:p-6 space-y-5">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl flex items-center justify-center"
              style={{ background: 'rgba(42,122,111,0.12)' }}>
              <Activity size={20} color="#2A7A6F" />
            </div>
            <div>
              <h1 className="text-xl font-bold" style={{ color: 'var(--text-primary)' }}>Prediction History</h1>
              <p className="text-xs" style={{ color: 'var(--text-muted)' }}>
                {total} predictions{winRate ? ` · ${winRate}% win rate` : ''}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <select value={symbol} onChange={e => { setSymbol(e.target.value); setPage(1); }}
              className="text-sm rounded-xl border px-3 py-2 outline-none"
              style={{ background: 'var(--bg-card)', borderColor: 'var(--border)', color: 'var(--text-primary)' }}>
              {SYMBOL_OPTS.map(s => <option key={s}>{s}</option>)}
            </select>
            <select value={horizon} onChange={e => { setHorizon(e.target.value); setPage(1); }}
              className="text-sm rounded-xl border px-3 py-2 outline-none"
              style={{ background: 'var(--bg-card)', borderColor: 'var(--border)', color: 'var(--text-primary)' }}>
              {HORIZON_OPTS.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
            </select>
            <button onClick={load} disabled={loading}
              className="p-2 rounded-xl border hover:bg-white/5" style={{ borderColor: 'var(--border)' }}>
              <RefreshCw size={14} className={loading ? 'animate-spin' : ''} style={{ color: 'var(--text-muted)' }} />
            </button>
          </div>
        </div>

        {error && (
          <div className="rounded-xl border border-red-500/30 p-4 text-sm text-red-400">{error}</div>
        )}

        {loading ? (
          <div className="rounded-xl border animate-pulse h-64"
            style={{ background: 'var(--bg-card)', borderColor: 'var(--border)' }} />
        ) : predictions.length === 0 ? (
          <div className="rounded-xl border p-14 text-center"
            style={{ background: 'var(--bg-card)', borderColor: 'var(--border)', color: 'var(--text-muted)' }}>
            <Activity size={44} className="mx-auto mb-4 opacity-30" />
            <p className="text-base font-semibold">No prediction history yet</p>
            <p className="text-sm mt-1">Generate predictions via the Predictions page</p>
          </div>
        ) : (
          <div className="rounded-xl border overflow-hidden" style={{ borderColor: 'var(--border)' }}>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead style={{ background: 'var(--bg-secondary)' }}>
                  <tr className="text-xs" style={{ color: 'var(--text-muted)', borderBottom: '1px solid var(--border)' }}>
                    {['Symbol', 'Horizon', 'Direction', 'Confidence', 'Expected Move', 'Outcome', 'Date'].map(h => (
                      <th key={h} className="px-4 py-2.5 text-left font-semibold">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody style={{ background: 'var(--bg-card)' }}>
                  {predictions.map((p, i) => <PredictionRow key={p.id || i} pred={p} />)}
                </tbody>
              </table>
            </div>
            {pagination && pagination.total_pages > 1 && (
              <div className="flex items-center justify-between px-4 py-3 border-t" style={{ borderColor: 'var(--border)' }}>
                <button disabled={page === 1} onClick={() => setPage(p => p - 1)}
                  className="text-xs px-3 py-1.5 rounded-lg border disabled:opacity-40"
                  style={{ borderColor: 'var(--border)', color: 'var(--text-secondary)' }}>← Previous</button>
                <span className="text-xs" style={{ color: 'var(--text-muted)' }}>
                  Page {page} of {pagination.total_pages}
                </span>
                <button disabled={page >= pagination.total_pages} onClick={() => setPage(p => p + 1)}
                  className="text-xs px-3 py-1.5 rounded-lg border disabled:opacity-40"
                  style={{ borderColor: 'var(--border)', color: 'var(--text-secondary)' }}>Next →</button>
              </div>
            )}
          </div>
        )}
      </div>
    </MainLayout>
  );
}
