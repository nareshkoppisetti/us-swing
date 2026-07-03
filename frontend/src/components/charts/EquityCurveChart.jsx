/**
 * File: frontend/src/components/charts/EquityCurveChart.jsx
 * Backtest equity curve with drawdown shading.
 * Props: equityCurve [{date, portfolio_value}], initialCapital
 */
'use client';
import { ComposedChart, Line, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, ReferenceLine } from 'recharts';

export default function EquityCurveChart({ equityCurve = [], initialCapital = 100000 }) {
  if (!equityCurve || equityCurve.length === 0) {
    return (
      <div className="text-center py-10 text-sm" style={{ color: 'var(--text-muted)' }}>
        No equity curve data available
      </div>
    );
  }
  let peak = initialCapital;
  const data = equityCurve.map(d => {
    peak = Math.max(peak, d.portfolio_value || 0);
    const drawdown = peak > 0 ? ((d.portfolio_value - peak) / peak) * 100 : 0;
    return {
      ...d,
      dateLabel: d.date ? new Date(d.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }) : '',
      drawdown,
    };
  });
  return (
    <ResponsiveContainer width="100%" height={260}>
      <ComposedChart data={data} margin={{ top: 5, right: 10, left: 0, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" opacity={0.3} vertical={false} />
        <XAxis dataKey="dateLabel" tick={{ fill: 'var(--text-muted)', fontSize: 10 }} axisLine={false} tickLine={false} minTickGap={30} />
        <YAxis tick={{ fill: 'var(--text-muted)', fontSize: 10 }} axisLine={false} tickLine={false} />
        <Tooltip contentStyle={{ background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 8, fontSize: 12 }} />
        <ReferenceLine y={initialCapital} stroke="var(--border)" strokeDasharray="3 3" label={{ value: 'Initial', fill: 'var(--text-muted)', fontSize: 10 }} />
        <Line type="monotone" dataKey="portfolio_value" stroke="#2A7A6F" strokeWidth={2} dot={false} name="Portfolio Value" />
      </ComposedChart>
    </ResponsiveContainer>
  );
}
