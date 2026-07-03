'use client';
export default function BearishDriversWidget({ factors }) {
  return (
    <div className="rounded-xl border p-4 h-full" style={{ background: 'var(--bg-card)', borderColor: 'var(--border)' }}>
      <div className="flex items-center justify-between mb-3">
        <span className="text-xs font-semibold uppercase tracking-wider" style={{ color: 'var(--text-muted)' }}>Bearish Risks</span>
        <span className="text-xs text-red-400">▼</span>
      </div>
      {factors?.length > 0 ? (
        <ul className="space-y-1.5">
          {factors.slice(0, 4).map((f, i) => (
            <li key={i} className="flex items-start gap-1.5 text-xs">
              <span className="text-red-400 mt-0.5 flex-shrink-0">•</span>
              <span style={{ color: 'var(--text-secondary)' }}>{typeof f === 'string' ? f : f.finding || f.factor}</span>
            </li>
          ))}
        </ul>
      ) : (
        <p className="text-xs" style={{ color: 'var(--text-muted)' }}>Generate a prediction to see risk factors.</p>
      )}
    </div>
  );
}
