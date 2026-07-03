'use client';
import { formatRelativeTime } from '@/lib/utils';
export default function PredictionTimeline({ predictions }) {
  return (
    <div className="rounded-xl border p-4 h-full" style={{ background: 'var(--bg-card)', borderColor: 'var(--border)' }}>
      <div className="flex items-center justify-between mb-3">
        <span className="text-xs font-semibold uppercase tracking-wider" style={{ color: 'var(--text-muted)' }}>Recent Predictions</span>
      </div>
      {predictions?.length > 0 ? (
        <div className="space-y-2">
          {predictions.slice(0, 5).map((p, i) => (
            <div key={p.id || i} className="flex items-center gap-2 text-xs">
              <span className={`w-2 h-2 rounded-full flex-shrink-0 ${p.direction === 'Bullish' ? 'bg-green-400' : p.direction === 'Bearish' ? 'bg-red-400' : 'bg-yellow-400'}`} />
              <span className="font-mono" style={{ color: 'var(--text-secondary)' }}>{p.symbol}</span>
              <span style={{ color: 'var(--text-muted)' }}>{p.horizon_days}D</span>
              <span className="flex-1" />
              <span style={{ color: 'var(--text-muted)' }}>{formatRelativeTime(p.created_at)}</span>
            </div>
          ))}
        </div>
      ) : (
        <p className="text-xs" style={{ color: 'var(--text-muted)' }}>No recent predictions.</p>
      )}
    </div>
  );
}
