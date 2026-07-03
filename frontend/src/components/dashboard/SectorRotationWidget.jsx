'use client';
/**
 * Wired to Agent 15 (Sector Rotation) actual output:
 *   supporting_data: { avg_sector_1m_return, leader: {name, return_1m}, laggard: {name, return_1m} }
 */
export default function SectorRotationWidget({ sectorData, agent15Data }) {
  // agent15Data = the full supporting_data from agent 15
  const leader  = agent15Data?.leader;
  const laggard = agent15Data?.laggard;
  const avg     = agent15Data?.avg_sector_1m_return;

  // Fallback: use generic sectorData prop (from charts page etc.)
  const sectors = sectorData || [];

  return (
    <div className="rounded-xl border p-4 h-full" style={{ background: 'var(--bg-card)', borderColor: 'var(--border)' }}>
      <div className="flex items-center justify-between mb-3">
        <span className="text-xs font-semibold uppercase tracking-wider" style={{ color: 'var(--text-muted)' }}>Sector Rotation</span>
      </div>

      {/* Agent 15 summary view */}
      {agent15Data ? (
        <div className="space-y-2 text-xs">
          {avg != null && (
            <div className="flex justify-between">
              <span style={{ color: 'var(--text-muted)' }}>Avg 1M Return</span>
              <span className={avg >= 0 ? 'text-green-400 font-semibold' : 'text-red-400 font-semibold'}>
                {avg >= 0 ? '+' : ''}{avg.toFixed(1)}%
              </span>
            </div>
          )}
          {leader?.name && (
            <div className="flex justify-between">
              <span style={{ color: 'var(--text-muted)' }}>Leader</span>
              <span className="text-green-400 font-semibold">
                {leader.name} {leader.return_1m != null ? `+${leader.return_1m.toFixed(1)}%` : ''}
              </span>
            </div>
          )}
          {laggard?.name && (
            <div className="flex justify-between">
              <span style={{ color: 'var(--text-muted)' }}>Laggard</span>
              <span className="text-red-400 font-semibold">
                {laggard.name} {laggard.return_1m != null ? `${laggard.return_1m.toFixed(1)}%` : ''}
              </span>
            </div>
          )}
        </div>
      ) : sectors.length > 0 ? (
        <div className="space-y-1">
          {sectors.slice(0, 5).map((s, i) => (
            <div key={s.symbol || i} className="flex items-center gap-2 text-xs">
              <span className="font-mono w-8 flex-shrink-0" style={{ color: 'var(--text-secondary)' }}>{s.symbol || s.name}</span>
              <div className="flex-1 h-1 rounded-full overflow-hidden" style={{ background: 'var(--border)' }}>
                <div className="h-full rounded-full"
                  style={{ width: `${Math.max(5, 100 - i * 15)}%`, background: (s.return_30d || 0) >= 0 ? '#22c55e' : '#ef4444' }} />
              </div>
              <span className={`w-10 text-right ${(s.return_30d || 0) >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                {s.return_30d != null ? `${Number(s.return_30d) >= 0 ? '+' : ''}${Number(s.return_30d).toFixed(1)}%` : '—'}
              </span>
            </div>
          ))}
        </div>
      ) : (
        <p className="text-xs" style={{ color: 'var(--text-muted)' }}>No sector data yet</p>
      )}
    </div>
  );
}
