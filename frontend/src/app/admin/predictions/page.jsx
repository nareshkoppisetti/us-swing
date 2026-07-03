'use client';
import { useState, useEffect } from 'react';
import { Brain, RefreshCw } from 'lucide-react';
import { api } from '@/lib/api';

const DIR_STYLE = {
  Bullish: 'text-green-400 bg-green-400/10 border-green-400/30',
  Bearish: 'text-red-400 bg-red-400/10 border-red-400/30',
  Neutral: 'text-yellow-400 bg-yellow-400/10 border-yellow-400/30',
};

export default function AdminPredictionsPage() {
  const [predictions, setPredictions] = useState([]);
  const [loading, setLoading] = useState(true);

  const load = () => {
    setLoading(true);
    api.getPredictions({ page_size: 50 })
      .then(d => setPredictions(d.data || []))
      .catch(() => {})
      .finally(() => setLoading(false));
  };

  useEffect(() => { load(); }, []);

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl flex items-center justify-center" style={{ background: 'rgba(198,40,40,0.1)' }}>
            <Brain size={20} color="#B5451B" />
          </div>
          <div>
            <h1 className="text-2xl font-bold" style={{ color: 'var(--text-primary)' }}>All Predictions</h1>
            <p className="text-sm" style={{ color: 'var(--text-muted)' }}>{predictions.length} recent predictions across all users</p>
          </div>
        </div>
        <button onClick={load} className="p-2 rounded-xl border hover:bg-white/5" style={{ borderColor: 'var(--border)' }}>
          <RefreshCw size={14} className={loading ? 'animate-spin' : ''} style={{ color: 'var(--text-muted)' }} />
        </button>
      </div>

      {loading ? (
        <div className="rounded-xl border animate-pulse h-64" style={{ background: 'var(--bg-card)', borderColor: 'var(--border)' }} />
      ) : predictions.length === 0 ? (
        <div className="rounded-xl border p-10 text-center" style={{ background: 'var(--bg-card)', borderColor: 'var(--border)', color: 'var(--text-muted)' }}>
          No predictions generated yet
        </div>
      ) : (
        <div className="rounded-xl border overflow-hidden" style={{ borderColor: 'var(--border)' }}>
          <table className="w-full text-sm">
            <thead style={{ background: 'var(--bg-secondary)' }}>
              <tr className="text-xs" style={{ color: 'var(--text-muted)', borderBottom: '1px solid var(--border)' }}>
                {['Symbol', 'Horizon', 'Direction', 'Confidence', 'Risk', 'Created'].map(h => (
                  <th key={h} className="px-4 py-2.5 text-left font-semibold">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody style={{ background: 'var(--bg-card)' }}>
              {predictions.map((p, i) => (
                <tr key={p.id || i} className="border-b last:border-0" style={{ borderColor: 'var(--border)' }}>
                  <td className="px-4 py-2.5 font-mono font-bold" style={{ color: '#2A7A6F' }}>{p.symbol}</td>
                  <td className="px-4 py-2.5 text-xs" style={{ color: 'var(--text-muted)' }}>{p.horizon_days}D</td>
                  <td className="px-4 py-2.5">
                    <span className={`text-xs px-2 py-0.5 rounded-full border font-semibold ${DIR_STYLE[p.direction] || DIR_STYLE.Neutral}`}>
                      {p.direction}
                    </span>
                  </td>
                  <td className="px-4 py-2.5" style={{ color: 'var(--text-secondary)' }}>{p.confidence?.toFixed(0)}%</td>
                  <td className="px-4 py-2.5" style={{ color: 'var(--text-secondary)' }}>{p.risk_score?.toFixed(0)}</td>
                  <td className="px-4 py-2.5 text-xs" style={{ color: 'var(--text-muted)' }}>
                    {p.created_at ? new Date(p.created_at).toLocaleString() : '—'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
