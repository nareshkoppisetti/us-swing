/**
 * File: frontend/src/components/charts/BreadthHistoryChart.jsx
 * Rolling market breadth history (% stocks above SMA50/200).
 * Props: breadthHistory [{date, pct_above_50, pct_above_200}], period
 */
'use client';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Legend } from 'recharts';

export default function BreadthHistoryChart({ breadthHistory = [], period = '30d' }) {
  if (!breadthHistory || breadthHistory.length === 0) {
    return (
      <div className="text-center py-10 text-sm" style={{ color: 'var(--text-muted)' }}>
        No breadth history available
      </div>
    );
  }
  const data = breadthHistory.map(d => ({
    ...d,
    dateLabel: d.date ? new Date(d.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }) : '',
  }));
  return (
    <ResponsiveContainer width="100%" height={260}>
      <LineChart data={data} margin={{ top: 5, right: 10, left: 0, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" opacity={0.3} vertical={false} />
        <XAxis dataKey="dateLabel" tick={{ fill: 'var(--text-muted)', fontSize: 10 }} axisLine={false} tickLine={false} minTickGap={30} />
        <YAxis domain={[0, 100]} unit="%" tick={{ fill: 'var(--text-muted)', fontSize: 10 }} axisLine={false} tickLine={false} />
        <Tooltip contentStyle={{ background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 8, fontSize: 12 }} />
        <Legend wrapperStyle={{ fontSize: 11, color: 'var(--text-muted)' }} />
        <Line type="monotone" dataKey="pct_above_50" name="% Above 50MA" stroke="#3b82f6" strokeWidth={2} dot={false} />
        <Line type="monotone" dataKey="pct_above_200" name="% Above 200MA" stroke="#f59e0b" strokeWidth={2} dot={false} />
      </LineChart>
    </ResponsiveContainer>
  );
}
