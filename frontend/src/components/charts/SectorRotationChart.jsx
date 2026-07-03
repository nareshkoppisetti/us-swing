/**
 * File: frontend/src/components/charts/SectorRotationChart.jsx
 * Relative sector performance bar chart (30d returns by sector ETF).
 * Props: sectorData [{symbol, name, return_30d}], period
 */
'use client';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell, CartesianGrid } from 'recharts';

export default function SectorRotationChart({ sectorData = [], period = '30d' }) {
  if (!sectorData || sectorData.length === 0) {
    return (
      <div className="text-center py-10 text-sm" style={{ color: 'var(--text-muted)' }}>
        No sector rotation data available
      </div>
    );
  }
  const sorted = [...sectorData].sort((a, b) => (b.return_30d || 0) - (a.return_30d || 0));
  return (
    <ResponsiveContainer width="100%" height={280}>
      <BarChart data={sorted} layout="vertical" margin={{ top: 5, right: 20, left: 10, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" opacity={0.3} horizontal={false} />
        <XAxis type="number" unit="%" tick={{ fill: 'var(--text-muted)', fontSize: 10 }} axisLine={false} tickLine={false} />
        <YAxis type="category" dataKey="symbol" tick={{ fill: 'var(--text-secondary)', fontSize: 11, fontFamily: 'monospace' }} axisLine={false} tickLine={false} width={50} />
        <Tooltip
          contentStyle={{ background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 8, fontSize: 12 }}
          formatter={(v) => [`${v >= 0 ? '+' : ''}${Number(v).toFixed(2)}%`, `${period} return`]}
        />
        <Bar dataKey="return_30d" radius={[0, 4, 4, 0]}>
          {sorted.map((entry, i) => (
            <Cell key={i} fill={(entry.return_30d || 0) >= 0 ? '#22c55e' : '#ef4444'} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
