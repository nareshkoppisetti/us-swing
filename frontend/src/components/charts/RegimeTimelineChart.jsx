/**
 * File: frontend/src/components/charts/RegimeTimelineChart.jsx
 * Historical market regime classification timeline (colored bands).
 * Props: regimeHistory [{date, regime}]
 */
'use client';

const REGIME_COLOR = {
  'Trending-Up': '#22c55e',
  'Trending-Down': '#ef4444',
  'Range-Bound': '#eab308',
  'Volatile': '#f97316',
  'Transitional': '#3b82f6',
  'Neutral': '#6b7280',
};

export default function RegimeTimelineChart({ regimeHistory = [] }) {
  if (!regimeHistory || regimeHistory.length === 0) {
    return (
      <div className="text-center py-10 text-sm" style={{ color: 'var(--text-muted)' }}>
        No regime history available
      </div>
    );
  }

  // Group consecutive same-regime days into bands
  const bands = [];
  let current = null;
  regimeHistory.forEach((d, i) => {
    if (!current || current.regime !== d.regime) {
      if (current) bands.push(current);
      current = { regime: d.regime, start: d.date, end: d.date, count: 1 };
    } else {
      current.end = d.date;
      current.count += 1;
    }
  });
  if (current) bands.push(current);

  const total = regimeHistory.length;

  return (
    <div>
      <div className="flex h-8 rounded-lg overflow-hidden">
        {bands.map((b, i) => (
          <div
            key={i}
            className="h-full"
            style={{ width: `${(b.count / total) * 100}%`, background: REGIME_COLOR[b.regime] || '#6b7280' }}
            title={`${b.regime}: ${b.start} → ${b.end}`}
          />
        ))}
      </div>
      <div className="flex items-center justify-between mt-2 text-xs" style={{ color: 'var(--text-muted)' }}>
        <span>{regimeHistory[0]?.date ? new Date(regimeHistory[0].date).toLocaleDateString() : ''}</span>
        <span>{regimeHistory[regimeHistory.length - 1]?.date ? new Date(regimeHistory[regimeHistory.length - 1].date).toLocaleDateString() : ''}</span>
      </div>
      <div className="flex flex-wrap gap-3 mt-3">
        {Object.entries(REGIME_COLOR).map(([label, color]) => (
          <span key={label} className="flex items-center gap-1.5 text-xs" style={{ color: 'var(--text-muted)' }}>
            <span className="w-2.5 h-2.5 rounded-sm" style={{ background: color }} />
            {label}
          </span>
        ))}
      </div>
    </div>
  );
}
