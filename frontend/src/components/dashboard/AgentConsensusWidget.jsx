'use client';
/**
 * Shows agent consensus from Agent 30 composite_score (0-100)
 * plus individual bull/bear/neutral counts from all agent outputs.
 */
export default function AgentConsensusWidget({ compositeScore, bullCount, bearCount, neutralCount }) {
  const pct = compositeScore ?? 50;
  const color = pct >= 65 ? '#22c55e' : pct >= 45 ? '#eab308' : '#ef4444';
  const label = pct >= 65 ? 'Bullish Consensus' : pct >= 45 ? 'Mixed' : 'Bearish Consensus';
  return (
    <div className="rounded-xl border p-4 h-full" style={{ background: 'var(--bg-card)', borderColor: 'var(--border)' }}>
      <div className="flex items-center justify-between mb-3">
        <span className="text-xs font-semibold uppercase tracking-wider" style={{ color: 'var(--text-muted)' }}>Agent Consensus</span>
      </div>
      <div className="text-3xl font-black" style={{ color }}>{pct.toFixed(0)}</div>
      <div className="text-xs mb-2" style={{ color }}>{label}</div>
      <div className="flex gap-3 text-xs">
        <span className="text-green-400">▲ {bullCount ?? 0} bull</span>
        <span className="text-red-400">▼ {bearCount ?? 0} bear</span>
        <span className="text-yellow-400">— {neutralCount ?? 0} neutral</span>
      </div>
    </div>
  );
}
