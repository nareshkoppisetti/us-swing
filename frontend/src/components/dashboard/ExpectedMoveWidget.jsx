'use client';
import { formatPct } from '@/lib/utils';
export default function ExpectedMoveWidget({ expectedMove, horizon = 5 }) {
  const val = expectedMove ?? 0;
  const isUp = val >= 0;
  return (
    <div className="rounded-xl border p-4 h-full" style={{ background: 'var(--bg-card)', borderColor: 'var(--border)' }}>
      <div className="flex items-center justify-between mb-3">
        <span className="text-xs font-semibold uppercase tracking-wider" style={{ color: 'var(--text-muted)' }}>Expected Move ({horizon}D)</span>
      </div>
      <div className={`text-3xl font-black ${isUp ? 'text-green-400' : 'text-red-400'}`}>{formatPct(val)}</div>
      <div className="text-xs mt-1" style={{ color: 'var(--text-muted)' }}>Based on ATR × horizon multiplier</div>
    </div>
  );
}
