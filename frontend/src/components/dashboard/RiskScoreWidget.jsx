'use client';
export default function RiskScoreWidget({ riskScore }) {
  const val = riskScore ?? 50;
  const color = val <= 35 ? '#22c55e' : val <= 65 ? '#eab308' : '#ef4444';
  const label = val <= 35 ? 'Low' : val <= 65 ? 'Moderate' : 'High';

  return (
    <div className="rounded-xl border p-4 h-full" style={{ background: 'var(--bg-card)', borderColor: 'var(--border)' }}>
      <div className="flex items-center justify-between mb-3">
        <span className="text-xs font-semibold uppercase tracking-wider" style={{ color: 'var(--text-muted)' }}>Risk Score</span>
      </div>
      <div className="flex items-center gap-3">
        <div className="text-3xl font-black" style={{ color }}>{val.toFixed(0)}</div>
        <div>
          <div className="text-sm font-semibold" style={{ color }}>{label} Risk</div>
          <div className="w-24 h-1.5 rounded-full mt-1.5 overflow-hidden" style={{ background: 'var(--border)' }}>
            <div className="h-full rounded-full transition-all" style={{ width: `${val}%`, background: color }} />
          </div>
        </div>
      </div>
    </div>
  );
}
