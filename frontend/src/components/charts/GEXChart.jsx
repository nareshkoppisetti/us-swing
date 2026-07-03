/**
 * File: frontend/src/components/charts/GEXChart.jsx
 * Gamma exposure profile by strike price.
 * Props: gexByStrike [{strike, gamma_exposure}], spotPrice
 */
'use client';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell, CartesianGrid, ReferenceLine } from 'recharts';

export default function GEXChart({ gexByStrike = [], spotPrice }) {
  if (!gexByStrike || gexByStrike.length === 0) {
    return (
      <div className="text-center py-10 text-sm" style={{ color: 'var(--text-muted)' }}>
        No gamma exposure data available
      </div>
    );
  }
  return (
    <ResponsiveContainer width="100%" height={260}>
      <BarChart data={gexByStrike} margin={{ top: 5, right: 10, left: 0, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" opacity={0.3} vertical={false} />
        <XAxis dataKey="strike" tick={{ fill: 'var(--text-muted)', fontSize: 10 }} axisLine={false} tickLine={false} />
        <YAxis tick={{ fill: 'var(--text-muted)', fontSize: 10 }} axisLine={false} tickLine={false}
          tickFormatter={(v) => `${(v / 1e6).toFixed(0)}M`} />
        <Tooltip contentStyle={{ background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 8, fontSize: 12 }}
          formatter={(v) => [`$${(v / 1e6).toFixed(1)}M`, 'GEX']} />
        {spotPrice && <ReferenceLine x={spotPrice} stroke="#2A7A6F" strokeDasharray="4 4" label={{ value: 'Spot', fill: '#2A7A6F', fontSize: 10 }} />}
        <Bar dataKey="gamma_exposure" radius={[2, 2, 0, 0]}>
          {gexByStrike.map((entry, i) => (
            <Cell key={i} fill={(entry.gamma_exposure || 0) >= 0 ? '#22c55e' : '#ef4444'} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
