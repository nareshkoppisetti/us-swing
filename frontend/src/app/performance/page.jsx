'use client';
/**
 * File: frontend/src/app/performance/page.jsx
 * Model accuracy and prediction performance tracking.
 * Integrates with backend /api/v1/performance/ endpoints.
 */
import { useState, useEffect, useCallback } from 'react';
import MainLayout from '@/components/layout/MainLayout';
import { api } from '@/lib/api';
import { Target, RefreshCw, TrendingUp, Award, BarChart2 } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell, LineChart, Line } from 'recharts';

const HORIZON_LABELS = { 2: '2D', 5: '5D', 10: '10D', 20: '20D', 30: '30D', 60: '60D' };
const SIGNAL_COLORS = { Bullish: '#22c55e', Bearish: '#ef4444', Neutral: '#eab308' };

function StatCard({ label, value, sub, color = 'var(--text-primary)' }) {
  return (
    <div className="rounded-xl border p-4" style={{ background: 'var(--bg-card)', borderColor: 'var(--border)' }}>
      <p className="text-xs font-semibold mb-1" style={{ color: 'var(--text-muted)' }}>{label}</p>
      <p className="text-2xl font-black" style={{ color }}>{value ?? '—'}</p>
      {sub && <p className="text-xs mt-0.5" style={{ color: 'var(--text-muted)' }}>{sub}</p>}
    </div>
  );
}

const SYMBOL_OPTS = ['SPY', 'QQQ', 'AAPL', 'TSLA', 'NVDA', 'GLD', 'ALL'];

export default function PerformancePage() {
  const [accuracy, setAccuracy] = useState(null);
  const [agentPerf, setAgentPerf] = useState([]);
  const [loading, setLoading] = useState(true);
  const [symbol, setSymbol] = useState('SPY');
  const [error, setError] = useState(null);

  const fetchData = useCallback(async () => {
    setLoading(true); setError(null);
    try {
      const params = symbol !== 'ALL' ? { symbol } : {};
      const [accRes, agentRes] = await Promise.allSettled([
        api.getAccuracy(params),
        api.getAgentPerformance(),
      ]);
      if (accRes.status === 'fulfilled') setAccuracy(accRes.value.data);
      if (agentRes.status === 'fulfilled') setAgentPerf(agentRes.value.data || []);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, [symbol]);

  useEffect(() => { fetchData(); }, [fetchData]);

  const overallWR = accuracy?.overall_win_rate ?? accuracy?.win_rate;
  const byHorizon = accuracy?.by_horizon || [];
  const totalPreds = accuracy?.total_predictions ?? accuracy?.total ?? 0;
  const avgReturn = accuracy?.avg_return_pct;

  // Chart data
  const horizonChartData = byHorizon.map(h => ({
    name: HORIZON_LABELS[h.horizon_days] || `${h.horizon_days}D`,
    winRate: ((h.win_rate || 0) * 100).toFixed(1),
    total: h.total_predictions || 0,
  }));

  const topAgents = [...agentPerf]
    .sort((a, b) => (b.accuracy_rate || 0) - (a.accuracy_rate || 0))
    .slice(0, 10);

  return (
    <MainLayout>
      <div className="p-4 md:p-6 space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl flex items-center justify-center"
              style={{ background: 'rgba(42,122,111,0.12)' }}>
              <Target size={20} color="#2A7A6F" />
            </div>
            <div>
              <h1 className="text-xl font-bold" style={{ color: 'var(--text-primary)' }}>Performance Analytics</h1>
              <p className="text-xs" style={{ color: 'var(--text-muted)' }}>Prediction accuracy and model performance</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <select value={symbol} onChange={e => setSymbol(e.target.value)}
              className="text-sm rounded-xl border px-3 py-2 outline-none"
              style={{ background: 'var(--bg-card)', borderColor: 'var(--border)', color: 'var(--text-primary)' }}>
              {SYMBOL_OPTS.map(s => <option key={s} value={s}>{s}</option>)}
            </select>
            <button onClick={fetchData} disabled={loading}
              className="p-2 rounded-xl border hover:bg-white/5 transition-colors"
              style={{ borderColor: 'var(--border)' }}>
              <RefreshCw size={14} className={loading ? 'animate-spin' : ''} style={{ color: 'var(--text-muted)' }} />
            </button>
          </div>
        </div>

        {error && (
          <div className="rounded-xl border border-red-500/30 p-4 text-sm text-red-400">{error}</div>
        )}

        {loading ? (
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="rounded-xl border animate-pulse h-24"
                style={{ background: 'var(--bg-card)', borderColor: 'var(--border)' }} />
            ))}
          </div>
        ) : (
          <>
            {/* Stats */}
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
              <StatCard
                label="Overall Win Rate"
                value={overallWR != null ? `${(overallWR * 100).toFixed(1)}%` : '—'}
                sub={`${totalPreds} predictions`}
                color={overallWR >= 0.55 ? '#22c55e' : overallWR >= 0.45 ? '#eab308' : '#ef4444'}
              />
              <StatCard
                label="Avg Return"
                value={avgReturn != null ? `${avgReturn >= 0 ? '+' : ''}${avgReturn.toFixed(2)}%` : '—'}
                sub="per prediction"
                color={avgReturn >= 0 ? '#22c55e' : '#ef4444'}
              />
              <StatCard
                label="Total Predictions"
                value={totalPreds.toLocaleString()}
                sub={symbol !== 'ALL' ? symbol : 'all symbols'}
              />
              <StatCard
                label="Best Horizon"
                value={byHorizon.length > 0
                  ? HORIZON_LABELS[byHorizon.reduce((a, b) => (a.win_rate || 0) > (b.win_rate || 0) ? a : b).horizon_days]
                  : '—'}
                sub="highest win rate"
                color="#2A7A6F"
              />
            </div>

            {/* Win Rate by Horizon Chart */}
            {horizonChartData.length > 0 && (
              <div className="rounded-xl border p-5" style={{ background: 'var(--bg-card)', borderColor: 'var(--border)' }}>
                <h2 className="text-sm font-semibold mb-4" style={{ color: 'var(--text-muted)' }}>
                  WIN RATE BY HORIZON
                </h2>
                <ResponsiveContainer width="100%" height={220}>
                  <BarChart data={horizonChartData} barCategoryGap="30%">
                    <XAxis dataKey="name" tick={{ fill: 'var(--text-muted)', fontSize: 12 }} axisLine={false} tickLine={false} />
                    <YAxis domain={[0, 100]} tick={{ fill: 'var(--text-muted)', fontSize: 12 }} axisLine={false} tickLine={false} unit="%" />
                    <Tooltip
                      contentStyle={{ background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 8 }}
                      formatter={(v) => [`${v}%`, 'Win Rate']}
                    />
                    <Bar dataKey="winRate" radius={[4, 4, 0, 0]}>
                      {horizonChartData.map((entry, i) => (
                        <Cell key={i}
                          fill={Number(entry.winRate) >= 55 ? '#22c55e' : Number(entry.winRate) >= 45 ? '#eab308' : '#ef4444'}
                        />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            )}

            {/* Top Agents Table */}
            {topAgents.length > 0 && (
              <div className="rounded-xl border overflow-hidden" style={{ borderColor: 'var(--border)' }}>
                <div className="px-5 py-3 border-b flex items-center gap-2"
                  style={{ borderColor: 'var(--border)', background: 'var(--bg-secondary)' }}>
                  <Award size={14} color="#2A7A6F" />
                  <h2 className="text-sm font-semibold" style={{ color: 'var(--text-primary)' }}>Top Performing Agents</h2>
                </div>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="text-xs" style={{ color: 'var(--text-muted)', borderBottom: '1px solid var(--border)' }}>
                        {['ID', 'Agent', 'Accuracy', 'Predictions', 'Avg Score'].map(h => (
                          <th key={h} className="px-4 py-2.5 text-left font-semibold">{h}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {topAgents.map((a, i) => (
                        <tr key={a.agent_id || i}
                          className="border-b last:border-0 hover:bg-white/5 transition-colors"
                          style={{ borderColor: 'var(--border)' }}>
                          <td className="px-4 py-2.5 font-mono text-xs" style={{ color: 'var(--text-muted)' }}>#{a.agent_id}</td>
                          <td className="px-4 py-2.5 font-medium" style={{ color: 'var(--text-primary)' }}>{a.agent_name}</td>
                          <td className="px-4 py-2.5">
                            <span className={`font-bold ${(a.accuracy_rate || 0) >= 0.6 ? 'text-green-400' : (a.accuracy_rate || 0) >= 0.5 ? 'text-yellow-400' : 'text-red-400'}`}>
                              {((a.accuracy_rate || 0) * 100).toFixed(1)}%
                            </span>
                          </td>
                          <td className="px-4 py-2.5" style={{ color: 'var(--text-secondary)' }}>
                            {a.total_predictions || 0}
                          </td>
                          <td className="px-4 py-2.5" style={{ color: 'var(--text-secondary)' }}>
                            {a.avg_score?.toFixed(1) ?? '—'}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {!accuracy && !loading && (
              <div className="rounded-xl border p-12 text-center"
                style={{ background: 'var(--bg-card)', borderColor: 'var(--border)', color: 'var(--text-muted)' }}>
                <BarChart2 size={44} className="mx-auto mb-4 opacity-30" />
                <p className="text-base font-semibold mb-2">No performance data yet</p>
                <p className="text-sm">Performance tracking activates after predictions are resolved</p>
              </div>
            )}
          </>
        )}
      </div>
    </MainLayout>
  );
}
