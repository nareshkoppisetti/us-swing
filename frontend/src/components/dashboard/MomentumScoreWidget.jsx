'use client';
export default function MomentumScoreWidget({ momentumScore, rsi, macdSignal }) {
  const score = momentumScore ?? 50;
  const color = score >= 60 ? '#22c55e' : score >= 40 ? '#eab308' : '#ef4444';
  return (
    <div className="rounded-xl border p-4 h-full" style={{ background: 'var(--bg-card)', borderColor: 'var(--border)' }}>
      <div className="flex items-center justify-between mb-3">
        <span className="text-xs font-semibold uppercase tracking-wider" style={{ color: 'var(--text-muted)' }}>Momentum</span>
      </div>
      <div className="text-3xl font-black" style={{ color }}>{score.toFixed(0)}</div>
      <div className="mt-2 grid grid-cols-2 gap-2 text-xs">
        <div><span style={{ color: 'var(--text-muted)' }}>RSI: </span><span style={{ color: 'var(--text-primary)' }}>{rsi?.toFixed(1) ?? '—'}</span></div>
        <div><span style={{ color: 'var(--text-muted)' }}>MACD: </span><span className={macdSignal >= 0 ? 'text-green-400' : 'text-red-400'}>{macdSignal != null ? (macdSignal >= 0 ? '▲' : '▼') : '—'}</span></div>
      </div>
    </div>
  );
}
