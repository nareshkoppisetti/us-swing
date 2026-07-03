'use client';
export default function HistoricalAccuracyWidget({ accuracy }) {
  const overall = accuracy?.overall_win_rate ?? accuracy?.win_rate;
  const byHorizon = accuracy?.by_horizon || [];
  const pct = overall != null ? (overall * 100).toFixed(1) : '—';
  const color = overall != null ? (overall >= 0.58 ? '#22c55e' : overall >= 0.50 ? '#eab308' : '#ef4444') : 'var(--text-muted)';
  return (
    <div className="rounded-xl border p-4 h-full" style={{ background: 'var(--bg-card)', borderColor: 'var(--border)' }}>
      <div className="flex items-center justify-between mb-3">
        <span className="text-xs font-semibold uppercase tracking-wider" style={{ color: 'var(--text-muted)' }}>Historical Accuracy</span>
      </div>
      <div className="text-3xl font-black" style={{ color }}>{pct}{overall != null ? '%' : ''}</div>
      <div className="mt-2 flex gap-2 flex-wrap">
        {byHorizon.slice(0, 3).map(h => (
          <span key={h.horizon_days} className="text-xs px-1.5 py-0.5 rounded" style={{ background: 'var(--bg-secondary)', color: 'var(--text-muted)' }}>
            {h.horizon_days}D: {((h.win_rate || 0) * 100).toFixed(0)}%
          </span>
        ))}
      </div>
    </div>
  );
}
