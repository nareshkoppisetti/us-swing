'use client';
/**
 * Wired to Agent 26 (VIX Structure) actual output:
 *   supporting_data: { vix, vix9d, vix3m, term_structure }
 */
export default function VIXStructureWidget({ vixLevel, vixStructure, score }) {
  const vix = vixLevel ?? 0;
  const color = vix < 15 ? '#22c55e' : vix < 20 ? '#eab308' : vix < 30 ? '#f97316' : '#ef4444';
  const label = vix < 15 ? 'Calm' : vix < 20 ? 'Normal' : vix < 30 ? 'Elevated' : 'Extreme Fear';
  return (
    <div className="rounded-xl border p-4 h-full" style={{ background: 'var(--bg-card)', borderColor: 'var(--border)' }}>
      <div className="flex items-center justify-between mb-3">
        <span className="text-xs font-semibold uppercase tracking-wider" style={{ color: 'var(--text-muted)' }}>VIX Structure</span>
      </div>
      <div className="flex items-end gap-2">
        <div className="text-3xl font-black" style={{ color }}>{vix.toFixed(1)}</div>
        <div className="text-sm mb-1" style={{ color }}>{label}</div>
      </div>
      <div className="mt-2 text-xs">
        <span style={{ color: 'var(--text-muted)' }}>Term Structure: </span>
        <span className={vixStructure === 'backwardation' ? 'text-red-400' : 'text-green-400'} style={{ fontWeight: 600 }}>
          {vixStructure || '—'}
        </span>
      </div>
      {score != null && (
        <div className="mt-1 text-xs">
          <span style={{ color: 'var(--text-muted)' }}>Score: </span>
          <span style={{ color: 'var(--text-primary)' }}>{score.toFixed(0)}/100</span>
        </div>
      )}
    </div>
  );
}
