/**
 * File: frontend/src/components/charts/AccuracyTrendChart.jsx
 * Rolling prediction accuracy/win-rate trend over time.
 * Props: accuracyHistory [{date, win_rate}], horizonLabel
 */
'use client';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, ReferenceLine } from 'recharts';

export default function AccuracyTrendChart({ accuracyHistory = [], horizonLabel = '' }) {
  if (!accuracyHistory || accuracyHistory.length === 0) {
    return (
      <div className="text-center py-10 text-sm" style={{ color: 'var(--text-muted)' }}>
        No accuracy trend data available
      </div>
    );
  }
  const data = accuracyHistory.map(d => ({
    ...d,
    dateLabel: d.date ? new Date(d.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }) : '',
    winRatePct: (d.win_rate || 0) * 100,
  }));
  return (
    <ResponsiveContainer width="100%" height={240}>
      <LineChart data={data} margin={{ top: 5, right: 10, left: 0, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" opacity={0.3} vertical={false} />
        <XAxis dataKey="dateLabel" tick={{ fill: 'var(--text-muted)', fontSize: 10 }} axisLine={false} tickLine={false} minTickGap={30} />
        <YAxis domain={[0, 100]} unit="%" tick={{ fill: 'var(--text-muted)', fontSize: 10 }} axisLine={false} tickLine={false} />
        <Tooltip contentStyle={{ background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 8, fontSize: 12 }}
          formatter={(v) => [`${Number(v).toFixed(1)}%`, `Win Rate ${horizonLabel}`]} />
        <ReferenceLine y={50} stroke="var(--border)" strokeDasharray="3 3" />
        <Line type="monotone" dataKey="winRatePct" stroke="#2A7A6F" strokeWidth={2} dot={false} />
      </LineChart>
    </ResponsiveContainer>
  );
}
