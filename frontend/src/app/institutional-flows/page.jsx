'use client';
/**
 * File: frontend/src/app/institutional-flows/page.jsx
 * Institutional flow intelligence — ETF flows, 13F, insider, dark pool.
 */
import { useState, useEffect } from 'react';
import MainLayout from '@/components/layout/MainLayout';
import { api } from '@/lib/api';
import { Building2, TrendingUp, TrendingDown, RefreshCw } from 'lucide-react';

const SYMBOLS = ['SPY', 'QQQ', 'AAPL', 'TSLA', 'NVDA', 'AMZN', 'META', 'MSFT'];

function Section({ title, children, loading }) {
  return (
    <div className="rounded-xl border overflow-hidden" style={{ borderColor: 'var(--border)' }}>
      <div className="px-5 py-3 border-b flex items-center gap-2"
        style={{ borderColor: 'var(--border)', background: 'var(--bg-secondary)' }}>
        <h2 className="text-sm font-semibold" style={{ color: 'var(--text-primary)' }}>{title}</h2>
      </div>
      <div className="p-4" style={{ background: 'var(--bg-card)' }}>
        {loading ? (
          <div className="space-y-2">{[...Array(3)].map((_, i) => (
            <div key={i} className="h-10 rounded-lg animate-pulse" style={{ background: 'var(--bg-secondary)' }} />
          ))}</div>
        ) : children}
      </div>
    </div>
  );
}

function InsiderRow({ t }) {
  const isBuy = t.transaction_type === 'Buy' || t.type === 'Buy';
  return (
    <div className="flex items-center gap-3 py-2 border-b last:border-0 text-xs" style={{ borderColor: 'var(--border)' }}>
      <span className="font-mono font-bold w-16 flex-shrink-0" style={{ color: 'var(--text-primary)' }}>{t.symbol}</span>
      <span className="flex-1" style={{ color: 'var(--text-secondary)' }}>{t.insider_name || t.name || '—'}</span>
      <span className={`font-semibold ${isBuy ? 'text-green-400' : 'text-red-400'}`}>{t.transaction_type || t.type || '—'}</span>
      <span style={{ color: 'var(--text-muted)' }}>${((t.value || t.amount || 0) / 1e6).toFixed(1)}M</span>
    </div>
  );
}

function ETFFlowRow({ flow }) {
  const isIn = (flow.net_flow || 0) >= 0;
  return (
    <div className="flex items-center gap-3 py-2 border-b last:border-0 text-xs" style={{ borderColor: 'var(--border)' }}>
      <span className="font-mono font-bold w-16 flex-shrink-0" style={{ color: 'var(--text-primary)' }}>{flow.symbol || flow.ticker}</span>
      <div className="flex-1 h-1.5 rounded-full overflow-hidden" style={{ background: 'var(--bg-secondary)' }}>
        <div className="h-full rounded-full" style={{
          width: `${Math.min(100, Math.abs(flow.net_flow || 0) / 1e8 * 100)}%`,
          background: isIn ? '#22c55e' : '#ef4444',
        }} />
      </div>
      <span className={`w-20 text-right font-semibold ${isIn ? 'text-green-400' : 'text-red-400'}`}>
        {isIn ? '+' : ''}{((flow.net_flow || 0) / 1e6).toFixed(0)}M
      </span>
    </div>
  );
}

export default function InstitutionalFlowsPage() {
  const [symbol, setSymbol] = useState('SPY');
  const [etfFlows, setEtfFlows] = useState(null);
  const [insider, setInsider] = useState([]);
  const [holdings13f, setHoldings13f] = useState([]);
  const [darkPool, setDarkPool] = useState(null);
  const [loading, setLoading] = useState({ etf: true, insider: false, f13: false, dark: false });

  useEffect(() => {
    // ETF flows for the selected symbol's sector
    setLoading(p => ({ ...p, etf: true }));
    api.getEtfFlows(symbol)
      .then(d => setEtfFlows(d.data))
      .catch(() => {})
      .finally(() => setLoading(p => ({ ...p, etf: false })));
  }, [symbol]);

  useEffect(() => {
    setLoading(p => ({ ...p, insider: true, f13: true, dark: true }));
    Promise.allSettled([
      api.getInsiderTransactions(symbol),
      api.get13fHoldings(symbol),
      api.getDarkPool(symbol),
    ]).then(([ins, f13, dp]) => {
      if (ins.status === 'fulfilled') setInsider(ins.value.data || []);
      if (f13.status === 'fulfilled') setHoldings13f(f13.value.data || []);
      if (dp.status === 'fulfilled') setDarkPool(dp.value.data);
    }).finally(() => setLoading(p => ({ ...p, insider: false, f13: false, dark: false })));
  }, [symbol]);

  const etfFlowList = Array.isArray(etfFlows) ? etfFlows : etfFlows?.flows || etfFlows?.etf_flows || [];

  return (
    <MainLayout>
      <div className="p-4 md:p-6 space-y-5">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl flex items-center justify-center"
              style={{ background: 'rgba(42,122,111,0.12)' }}>
              <Building2 size={20} color="#2A7A6F" />
            </div>
            <div>
              <h1 className="text-xl font-bold" style={{ color: 'var(--text-primary)' }}>Institutional Flows</h1>
              <p className="text-xs" style={{ color: 'var(--text-muted)' }}>13F, insider activity, ETF flows, dark pool</p>
            </div>
          </div>
          <select value={symbol} onChange={e => setSymbol(e.target.value)}
            className="text-sm rounded-xl border px-3 py-2 outline-none"
            style={{ background: 'var(--bg-card)', borderColor: 'var(--border)', color: 'var(--text-primary)' }}>
            {SYMBOLS.map(s => <option key={s}>{s}</option>)}
          </select>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
          {/* ETF Flows */}
          <Section title="ETF Capital Flows" loading={loading.etf}>
            {etfFlowList.length > 0 ? (
              <div className="space-y-0">
                {etfFlowList.slice(0, 10).map((f, i) => <ETFFlowRow key={i} flow={f} />)}
              </div>
            ) : (
              <p className="text-sm text-center py-4" style={{ color: 'var(--text-muted)' }}>
                ETF flow data not available (backend stub)
              </p>
            )}
          </Section>

          {/* Insider Transactions */}
          <Section title={`Insider Transactions — ${symbol}`} loading={loading.insider}>
            {insider.length > 0 ? (
              <div className="space-y-0">
                {insider.slice(0, 10).map((t, i) => <InsiderRow key={i} t={t} />)}
              </div>
            ) : (
              <p className="text-sm text-center py-4" style={{ color: 'var(--text-muted)' }}>
                No insider transactions found for {symbol}
              </p>
            )}
          </Section>

          {/* 13F Holdings */}
          <Section title={`13F Institutional Holdings — ${symbol}`} loading={loading.f13}>
            {holdings13f.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="w-full text-xs">
                  <thead>
                    <tr style={{ color: 'var(--text-muted)', borderBottom: '1px solid var(--border)' }}>
                      {['Institution', 'Shares', 'Value', 'Change'].map(h => (
                        <th key={h} className="py-2 text-left font-semibold">{h}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {holdings13f.slice(0, 8).map((h, i) => (
                      <tr key={i} className="border-b last:border-0" style={{ borderColor: 'var(--border)' }}>
                        <td className="py-2" style={{ color: 'var(--text-primary)' }}>{h.institution || h.fund_name}</td>
                        <td className="py-2" style={{ color: 'var(--text-secondary)' }}>{h.shares?.toLocaleString()}</td>
                        <td className="py-2" style={{ color: 'var(--text-secondary)' }}>${((h.value || 0) / 1e6).toFixed(1)}M</td>
                        <td className={`py-2 font-semibold ${(h.change || 0) >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                          {h.change != null ? `${h.change >= 0 ? '+' : ''}${h.change.toFixed(1)}%` : '—'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <p className="text-sm text-center py-4" style={{ color: 'var(--text-muted)' }}>
                No 13F data available for {symbol}
              </p>
            )}
          </Section>

          {/* Dark Pool */}
          <Section title={`Dark Pool Activity — ${symbol}`} loading={loading.dark}>
            {darkPool ? (
              <div className="grid grid-cols-2 gap-3 text-xs">
                {[
                  { label: 'Dark Pool %', value: darkPool.dark_pool_pct != null ? `${darkPool.dark_pool_pct.toFixed(1)}%` : '—' },
                  { label: 'Signal', value: darkPool.signal || '—', color: darkPool.signal === 'Bullish' ? '#22c55e' : darkPool.signal === 'Bearish' ? '#ef4444' : '#eab308' },
                  { label: 'Large Prints', value: darkPool.large_print_count ?? '—' },
                  { label: 'Score', value: darkPool.score?.toFixed(0) ?? '—' },
                ].map(({ label, value, color }) => (
                  <div key={label} className="rounded-lg p-3" style={{ background: 'var(--bg-secondary)' }}>
                    <p className="text-xs mb-1" style={{ color: 'var(--text-muted)' }}>{label}</p>
                    <p className="font-bold" style={{ color: color || 'var(--text-primary)' }}>{value}</p>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-center py-4" style={{ color: 'var(--text-muted)' }}>
                No dark pool data available
              </p>
            )}
          </Section>
        </div>
      </div>
    </MainLayout>
  );
}
