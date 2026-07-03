'use client';
/**
 * Wired to Agent 20 (ETF Flow Intelligence) actual output:
 *   supporting_data: { etf_scores_avg, etfs_checked, sector_etf }
 */
export default function ETFFlowSummary({ etfFlows }) {
  const score        = etfFlows?.etf_scores_avg ?? etfFlows?.etf_flow_score ?? 50;
  const etfsChecked  = etfFlows?.etfs_checked;
  const topSector    = etfFlows?.sector_etf;
  const up = score >= 55;

  return (
    <div className="rounded-xl border p-4 h-full" style={{ background: 'var(--bg-card)', borderColor: 'var(--border)' }}>
      <div className="flex items-center justify-between mb-3">
        <span className="text-xs font-semibold uppercase tracking-wider" style={{ color: 'var(--text-muted)' }}>ETF Flows</span>
      </div>
      <div className={`text-xl font-bold ${up ? 'text-green-400' : 'text-red-400'}`}>
        {up ? 'Net Inflow' : 'Net Outflow'}
      </div>
      <div className="mt-2 space-y-1 text-xs">
        <div className="flex justify-between">
          <span style={{ color: 'var(--text-muted)' }}>Flow Score</span>
          <span className={up ? 'text-green-400' : 'text-red-400'} style={{ fontWeight: 600 }}>
            {score.toFixed(0)}/100
          </span>
        </div>
        {etfsChecked != null && (
          <div className="flex justify-between">
            <span style={{ color: 'var(--text-muted)' }}>ETFs tracked</span>
            <span style={{ color: 'var(--text-secondary)' }}>{etfsChecked}</span>
          </div>
        )}
        {topSector && (
          <div className="flex justify-between">
            <span style={{ color: 'var(--text-muted)' }}>Top sector</span>
            <span className="font-mono font-bold" style={{ color: '#2A7A6F' }}>{topSector}</span>
          </div>
        )}
      </div>
    </div>
  );
}
