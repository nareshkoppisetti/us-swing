'use client';
export default function MarketBreadthWidget({ breadthScore, pctAbove20d, pctAbove50d, pctAbove200d }) {
  const score = breadthScore ?? 50;
  const color = score >= 60 ? '#22c55e' : score >= 40 ? '#eab308' : '#ef4444';
  return (
    <div className="rounded-xl border p-4 h-full" style={{ background: 'var(--bg-card)', borderColor: 'var(--border)' }}>
      <div className="flex items-center justify-between mb-3">
        <span className="text-xs font-semibold uppercase tracking-wider" style={{ color: 'var(--text-muted)' }}>Market Breadth</span>
      </div>
      <div className="text-3xl font-black" style={{ color }}>{score.toFixed(0)}</div>
      <div className="mt-3 space-y-1.5">
        {[['Above 20MA', pctAbove20d], ['Above 50MA', pctAbove50d], ['Above 200MA', pctAbove200d]].map(([label, val]) => (
          <div key={label} className="flex items-center gap-2">
            <span className="text-xs w-24 flex-shrink-0" style={{ color: 'var(--text-muted)' }}>{label}</span>
            <div className="flex-1 h-1 rounded-full overflow-hidden" style={{ background: 'var(--border)' }}>
              <div className="h-full rounded-full" style={{ width: `${val ?? 50}%`, background: color }} />
            </div>
            <span className="text-xs w-10 text-right" style={{ color: 'var(--text-secondary)' }}>{val != null ? `${val.toFixed(0)}%` : '—'}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
