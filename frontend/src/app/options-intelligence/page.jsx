'use client';
/**
 * File: frontend/src/app/options-intelligence/page.jsx
 * Options intelligence — GEX, OI structure, put/call, VIX.
 */
import { useState, useEffect, useMemo } from 'react';
import MainLayout from '@/components/layout/MainLayout';
import { api } from '@/lib/api';
import { LineChart as LCIcon, RefreshCw } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';

const SYMBOLS = ['SPY', 'QQQ', 'AAPL', 'TSLA', 'NVDA', 'AMZN', 'META', 'MSFT'];

function InfoCard({ label, value, color, sub }) {
  return (
    <div className="rounded-xl border p-4" style={{ background: 'var(--bg-card)', borderColor: 'var(--border)' }}>
      <p className="text-xs font-semibold mb-1" style={{ color: 'var(--text-muted)' }}>{label}</p>
      <p className="text-2xl font-black" style={{ color: color || 'var(--text-primary)' }}>{value ?? '—'}</p>
      {sub && <p className="text-xs mt-0.5" style={{ color: 'var(--text-muted)' }}>{sub}</p>}
    </div>
  );
}

/**
 * There is no standalone "OI structure" backend endpoint — the options
 * chain endpoint (/options/chain) carries open_interest per row (per
 * strike + expiry + option_type). This aggregates the raw chain rows
 * into { strikes: [{ strike, call_oi, put_oi }], put_call_ratio }
 * across all expiries, which is what this page's chart/metrics need.
 */
function buildOIStructure(chainRows) {
  if (!Array.isArray(chainRows) || chainRows.length === 0) return null;

  const byStrike = new Map();
  let totalCallOI = 0;
  let totalPutOI = 0;

  for (const row of chainRows) {
    const strike = row.strike;
    if (strike == null) continue;
    const oi = row.open_interest || 0;

    if (!byStrike.has(strike)) {
      byStrike.set(strike, { strike, call_oi: 0, put_oi: 0 });
    }
    const entry = byStrike.get(strike);

    if (row.option_type === 'call') {
      entry.call_oi += oi;
      totalCallOI += oi;
    } else if (row.option_type === 'put') {
      entry.put_oi += oi;
      totalPutOI += oi;
    }
  }

  const strikes = Array.from(byStrike.values()).sort((a, b) => a.strike - b.strike);

  return {
    strikes,
    put_call_ratio: totalCallOI > 0 ? totalPutOI / totalCallOI : null,
  };
}

export default function OptionsPage() {
  const [symbol, setSymbol] = useState('SPY');
  const [gex, setGex] = useState(null);
  const [chain, setChain] = useState(null);
  const [vix, setVix] = useState(null);
  const [loading, setLoading] = useState(false);

  const load = async () => {
    setLoading(true);
    await Promise.allSettled([
      api.getGEX(symbol).then(d => setGex(d.data)),
      api.getOptionsChain(symbol).then(d => setChain(d.data)),
      api.getVIX().then(d => setVix(d.data)),
    ]);
    setLoading(false);
  };

  useEffect(() => { load(); }, [symbol]);

  const oi = useMemo(() => buildOIStructure(chain), [chain]);

  const gexLevel = gex?.gamma_exposure ?? gex?.gex_value;
  const vixLevel = vix?.vix ?? vix?.vix_current;
  const pcRatio = oi?.put_call_ratio ?? gex?.put_call_ratio;
  const maxPain = gex?.max_pain_strike ?? oi?.max_pain;

  // OI chart data
  const oiChartData = (oi?.strikes || []).slice(0, 20).map(s => ({
    strike: s.strike,
    calls: s.call_oi || 0,
    puts: s.put_oi || 0,
  }));

  return (
    <MainLayout>
      <div className="p-4 md:p-6 space-y-5">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl flex items-center justify-center"
              style={{ background: 'rgba(42,122,111,0.12)' }}>
              <LCIcon size={20} color="#2A7A6F" />
            </div>
            <div>
              <h1 className="text-xl font-bold" style={{ color: 'var(--text-primary)' }}>Options Intelligence</h1>
              <p className="text-xs" style={{ color: 'var(--text-muted)' }}>GEX, OI structure, put/call, volatility</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <select value={symbol} onChange={e => setSymbol(e.target.value)}
              className="text-sm rounded-xl border px-3 py-2 outline-none"
              style={{ background: 'var(--bg-card)', borderColor: 'var(--border)', color: 'var(--text-primary)' }}>
              {SYMBOLS.map(s => <option key={s}>{s}</option>)}
            </select>
            <button onClick={load} disabled={loading}
              className="p-2 rounded-xl border hover:bg-white/5" style={{ borderColor: 'var(--border)' }}>
              <RefreshCw size={14} className={loading ? 'animate-spin' : ''} style={{ color: 'var(--text-muted)' }} />
            </button>
          </div>
        </div>

        {/* Key metrics */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <InfoCard label="VIX" value={vixLevel?.toFixed(2) ?? '—'}
            color={vixLevel < 15 ? '#22c55e' : vixLevel < 25 ? '#eab308' : '#ef4444'}
            sub={vixLevel < 15 ? 'Low vol' : vixLevel < 25 ? 'Normal' : 'Elevated'} />
          <InfoCard label="Put/Call Ratio" value={pcRatio?.toFixed(2) ?? '—'}
            color={pcRatio > 1.2 ? '#ef4444' : pcRatio < 0.7 ? '#22c55e' : '#eab308'}
            sub={pcRatio > 1 ? 'Put-heavy' : 'Call-heavy'} />
          <InfoCard label="Gamma Exposure" value={gexLevel != null ? `$${(gexLevel / 1e9).toFixed(1)}B` : '—'}
            color={gexLevel >= 0 ? '#22c55e' : '#ef4444'}
            sub={gexLevel >= 0 ? 'Positive GEX' : 'Negative GEX'} />
          <InfoCard label="Max Pain" value={maxPain != null ? `$${maxPain}` : '—'}
            sub="OI-weighted strike" />
        </div>

        {/* OI Chart */}
        {oiChartData.length > 0 ? (
          <div className="rounded-xl border p-5" style={{ background: 'var(--bg-card)', borderColor: 'var(--border)' }}>
            <h2 className="text-sm font-semibold mb-4" style={{ color: 'var(--text-muted)' }}>
              OPEN INTEREST BY STRIKE — {symbol}
            </h2>
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={oiChartData} barCategoryGap="20%">
                <XAxis dataKey="strike" tick={{ fill: 'var(--text-muted)', fontSize: 10 }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fill: 'var(--text-muted)', fontSize: 10 }} axisLine={false} tickLine={false} />
                <Tooltip contentStyle={{ background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 8 }} />
                <Bar dataKey="calls" fill="#22c55e" radius={[2, 2, 0, 0]} name="Calls OI" />
                <Bar dataKey="puts" fill="#ef4444" radius={[2, 2, 0, 0]} name="Puts OI" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        ) : (
          <div className="rounded-xl border p-12 text-center"
            style={{ background: 'var(--bg-card)', borderColor: 'var(--border)', color: 'var(--text-muted)' }}>
            <LCIcon size={44} className="mx-auto mb-4 opacity-30" />
            <p className="text-base font-semibold mb-2">Options data not available</p>
            <p className="text-sm">Options endpoints will be implemented in a future phase</p>
          </div>
        )}

        {/* GEX Detail */}
        {gex && (
          <div className="rounded-xl border p-5" style={{ background: 'var(--bg-card)', borderColor: 'var(--border)' }}>
            <h2 className="text-sm font-semibold mb-3" style={{ color: 'var(--text-muted)' }}>GEX ANALYSIS</h2>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-3 text-xs">
              {[
                { label: 'GEX Signal', value: gex.signal || '—' },
                { label: 'Key Support', value: gex.support_level != null ? `$${gex.support_level}` : '—' },
                { label: 'Key Resistance', value: gex.resistance_level != null ? `$${gex.resistance_level}` : '—' },
                { label: 'Implied Move', value: gex.implied_move_pct != null ? `±${gex.implied_move_pct.toFixed(1)}%` : '—' },
                { label: 'Vol Regime', value: gex.vol_regime || '—' },
                { label: 'Score', value: gex.score?.toFixed(0) ?? '—' },
              ].map(({ label, value }) => (
                <div key={label} className="rounded-lg p-3" style={{ background: 'var(--bg-secondary)' }}>
                  <p style={{ color: 'var(--text-muted)' }}>{label}</p>
                  <p className="font-semibold mt-0.5" style={{ color: 'var(--text-primary)' }}>{value}</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </MainLayout>
  );
}
