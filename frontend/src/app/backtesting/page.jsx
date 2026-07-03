'use client';
/**
 * File: frontend/src/app/backtesting/page.jsx
 * Backtesting engine — run signal backtests and view equity curves.
 */
import { useState } from 'react';
import MainLayout from '@/components/layout/MainLayout';
import { api } from '@/lib/api';
import { History, Play, TrendingUp, BarChart2 } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, ReferenceLine } from 'recharts';

function StatCard({ label, value, color = 'var(--text-primary)', sub }) {
  return (
    <div className="rounded-xl border p-4" style={{ background: 'var(--bg-card)', borderColor: 'var(--border)' }}>
      <p className="text-xs font-semibold mb-1" style={{ color: 'var(--text-muted)' }}>{label}</p>
      <p className="text-2xl font-black" style={{ color }}>{value ?? '—'}</p>
      {sub && <p className="text-xs mt-0.5" style={{ color: 'var(--text-muted)' }}>{sub}</p>}
    </div>
  );
}

const HORIZONS = [2, 5, 10, 20, 30, 60];
const SYMBOLS = ['SPY', 'QQQ', 'AAPL', 'TSLA', 'NVDA', 'GLD', 'AMZN', 'META'];

export default function BacktestingPage() {
  const [form, setForm] = useState({ symbol: 'SPY', horizon_days: 5, lookback_days: 365, initial_capital: 100000 });
  const [running, setRunning] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleRun = async () => {
    setRunning(true); setError(null);
    try {
      const today = new Date();
      const start = new Date(today.getTime() - form.lookback_days * 24 * 60 * 60 * 1000);
      const res = await api.runBacktest({
        symbol: form.symbol,
        horizon_days: form.horizon_days,
        start_date: start.toISOString().slice(0, 10),
        end_date: today.toISOString().slice(0, 10),
        confidence_threshold: 65,
      });
      setResult(res.data?.results || null);
    } catch (e) {
      setError(e.message);
    } finally {
      setRunning(false);
    }
  };

  const equity = (result?.equity_curve || []).map(pt => ({
    date: pt.date,
    portfolio_value: form.initial_capital * (1 + pt.cumulative_return / 100),
  }));
  const totalReturn = result?.total_return_pct;
  const winRate = result?.win_rate;
  const maxDrawdown = result?.max_drawdown_pct;
  const sharpe = result?.sharpe_ratio;
  const trades = result?.total_trades;

  return (
    <MainLayout>
      <div className="p-4 md:p-6 space-y-6">
        {/* Header */}
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl flex items-center justify-center"
            style={{ background: 'rgba(42,122,111,0.12)' }}>
            <History size={20} color="#2A7A6F" />
          </div>
          <div>
            <h1 className="text-xl font-bold" style={{ color: 'var(--text-primary)' }}>Backtesting Engine</h1>
            <p className="text-xs" style={{ color: 'var(--text-muted)' }}>Signal strategy backtesting</p>
          </div>
        </div>

        {/* Config Panel */}
        <div className="rounded-xl border p-5 grid grid-cols-2 md:grid-cols-4 gap-4"
          style={{ background: 'var(--bg-card)', borderColor: 'var(--border)' }}>
          <div>
            <label className="text-xs font-semibold block mb-1.5" style={{ color: 'var(--text-muted)' }}>Symbol</label>
            <select value={form.symbol} onChange={e => setForm(p => ({ ...p, symbol: e.target.value }))}
              className="w-full rounded-lg border px-3 py-2 text-sm outline-none"
              style={{ background: 'var(--bg-secondary)', borderColor: 'var(--border)', color: 'var(--text-primary)' }}>
              {SYMBOLS.map(s => <option key={s}>{s}</option>)}
            </select>
          </div>
          <div>
            <label className="text-xs font-semibold block mb-1.5" style={{ color: 'var(--text-muted)' }}>Horizon (days)</label>
            <select value={form.horizon_days} onChange={e => setForm(p => ({ ...p, horizon_days: Number(e.target.value) }))}
              className="w-full rounded-lg border px-3 py-2 text-sm outline-none"
              style={{ background: 'var(--bg-secondary)', borderColor: 'var(--border)', color: 'var(--text-primary)' }}>
              {HORIZONS.map(h => <option key={h} value={h}>{h}D</option>)}
            </select>
          </div>
          <div>
            <label className="text-xs font-semibold block mb-1.5" style={{ color: 'var(--text-muted)' }}>Lookback (days)</label>
            <select value={form.lookback_days} onChange={e => setForm(p => ({ ...p, lookback_days: Number(e.target.value) }))}
              className="w-full rounded-lg border px-3 py-2 text-sm outline-none"
              style={{ background: 'var(--bg-secondary)', borderColor: 'var(--border)', color: 'var(--text-primary)' }}>
              {[90, 180, 365, 730].map(d => <option key={d} value={d}>{d}D</option>)}
            </select>
          </div>
          <div className="flex items-end">
            <button onClick={handleRun} disabled={running}
              className="w-full flex items-center justify-center gap-2 px-4 py-2 rounded-xl text-sm font-semibold text-white disabled:opacity-50"
              style={{ background: '#2A7A6F' }}>
              <Play size={13} />
              {running ? 'Running…' : 'Run Backtest'}
            </button>
          </div>
        </div>

        {error && (
          <div className="rounded-xl border border-red-500/30 p-4 text-sm text-red-400">{error}</div>
        )}

        {result && (
          <>
            {/* Stats */}
            <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
              <StatCard label="Total Return"
                value={totalReturn != null ? `${totalReturn >= 0 ? '+' : ''}${totalReturn.toFixed(2)}%` : '—'}
                color={totalReturn >= 0 ? '#22c55e' : '#ef4444'} />
              <StatCard label="Win Rate"
                value={winRate != null ? `${(winRate * 100).toFixed(1)}%` : '—'}
                color={winRate >= 0.55 ? '#22c55e' : '#eab308'} />
              <StatCard label="Max Drawdown"
                value={maxDrawdown != null ? `-${Math.abs(maxDrawdown).toFixed(2)}%` : '—'}
                color="#ef4444" />
              <StatCard label="Sharpe Ratio"
                value={sharpe?.toFixed(2) ?? '—'}
                color={sharpe >= 1 ? '#22c55e' : sharpe >= 0 ? '#eab308' : '#ef4444'} />
              <StatCard label="Total Trades" value={trades ?? '—'} />
            </div>

            {/* Equity Curve */}
            {equity.length > 0 && (
              <div className="rounded-xl border p-5" style={{ background: 'var(--bg-card)', borderColor: 'var(--border)' }}>
                <h2 className="text-sm font-semibold mb-4" style={{ color: 'var(--text-muted)' }}>EQUITY CURVE</h2>
                <ResponsiveContainer width="100%" height={240}>
                  <LineChart data={equity}>
                    <XAxis dataKey="date" tick={{ fill: 'var(--text-muted)', fontSize: 11 }} axisLine={false} tickLine={false} />
                    <YAxis tick={{ fill: 'var(--text-muted)', fontSize: 11 }} axisLine={false} tickLine={false} />
                    <Tooltip
                      contentStyle={{ background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 8 }}
                    />
                    <ReferenceLine y={form.initial_capital} stroke="var(--border)" strokeDasharray="3 3" />
                    <Line type="monotone" dataKey="portfolio_value" stroke="#2A7A6F" strokeWidth={2} dot={false} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            )}

            {/* Trades table */}
            {result?.trades?.length > 0 && (
              <div className="rounded-xl border overflow-hidden" style={{ borderColor: 'var(--border)' }}>
                <div className="px-5 py-3 border-b" style={{ borderColor: 'var(--border)', background: 'var(--bg-secondary)' }}>
                  <h2 className="text-sm font-semibold" style={{ color: 'var(--text-primary)' }}>Trade Log</h2>
                </div>
                <div className="overflow-x-auto max-h-64">
                  <table className="w-full text-xs">
                    <thead style={{ background: 'var(--bg-secondary)' }}>
                      <tr style={{ color: 'var(--text-muted)', borderBottom: '1px solid var(--border)' }}>
                        {['Date', 'Signal', 'Entry', 'Exit', 'Return', 'Outcome'].map(h => (
                          <th key={h} className="px-4 py-2 text-left font-semibold">{h}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody style={{ background: 'var(--bg-card)' }}>
                      {result.trades.map((t, i) => (
                        <tr key={i} className="border-b last:border-0" style={{ borderColor: 'var(--border)' }}>
                          <td className="px-4 py-2" style={{ color: 'var(--text-muted)' }}>{t.entry_date}</td>
                          <td className="px-4 py-2">
                            <span className={t.signal === 'Bullish' ? 'text-green-400' : t.signal === 'Bearish' ? 'text-red-400' : 'text-yellow-400'}>
                              {t.signal}
                            </span>
                          </td>
                          <td className="px-4 py-2" style={{ color: 'var(--text-secondary)' }}>${t.entry_price?.toFixed(2)}</td>
                          <td className="px-4 py-2" style={{ color: 'var(--text-secondary)' }}>${t.exit_price?.toFixed(2)}</td>
                          <td className={`px-4 py-2 font-semibold ${(t.return_pct || 0) >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                            {t.return_pct != null ? `${t.return_pct >= 0 ? '+' : ''}${t.return_pct.toFixed(2)}%` : '—'}
                          </td>
                          <td className="px-4 py-2">
                            {t.correct ? <span className="text-green-400">✓</span> : <span className="text-red-400">✗</span>}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </>
        )}

        {!result && !running && (
          <div className="rounded-xl border p-14 text-center"
            style={{ background: 'var(--bg-card)', borderColor: 'var(--border)', color: 'var(--text-muted)' }}>
            <BarChart2 size={44} className="mx-auto mb-4 opacity-30" />
            <p className="text-base font-semibold mb-2">Configure and run a backtest</p>
            <p className="text-sm">Select a symbol, horizon, and lookback period then click Run</p>
          </div>
        )}
      </div>
    </MainLayout>
  );
}
