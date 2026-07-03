'use client';
/**
 * Wired to Agent 18 (Whale Options Flow) actual output:
 *   supporting_data: { call_vol, put_vol, call_oi, put_oi, pc_oi_ratio, pc_vol_ratio }
 *                  + unusual_call, unusual_put (booleans)
 */
export default function WhaleFlowSummary({ whaleData }) {
  const signal    = whaleData?.whale_flow_signal || whaleData?.signal || 'Neutral';
  const pcVol     = whaleData?.pc_vol_ratio;
  const pcOi      = whaleData?.pc_oi_ratio;
  const unusualCall = whaleData?.unusual_call;
  const unusualPut  = whaleData?.unusual_put;
  const up   = signal === 'Bullish';
  const down = signal === 'Bearish';

  return (
    <div className="rounded-xl border p-4 h-full" style={{ background: 'var(--bg-card)', borderColor: 'var(--border)' }}>
      <div className="flex items-center justify-between mb-3">
        <span className="text-xs font-semibold uppercase tracking-wider" style={{ color: 'var(--text-muted)' }}>Whale Flow</span>
      </div>
      <div className={`text-xl font-bold ${up ? 'text-green-400' : down ? 'text-red-400' : 'text-yellow-400'}`}>
        {signal}
      </div>
      <div className="mt-2 space-y-1 text-xs">
        {pcVol != null && (
          <div className="flex justify-between">
            <span style={{ color: 'var(--text-muted)' }}>P/C Vol Ratio</span>
            <span className={pcVol > 1 ? 'text-red-400' : 'text-green-400'} style={{ fontWeight: 600 }}>
              {pcVol.toFixed(2)}
            </span>
          </div>
        )}
        {pcOi != null && (
          <div className="flex justify-between">
            <span style={{ color: 'var(--text-muted)' }}>P/C OI Ratio</span>
            <span style={{ color: 'var(--text-secondary)', fontWeight: 600 }}>{pcOi.toFixed(2)}</span>
          </div>
        )}
        {unusualCall && (
          <div className="text-green-400">⚡ Unusual call activity detected</div>
        )}
        {unusualPut && (
          <div className="text-red-400">⚡ Unusual put activity detected</div>
        )}
        {pcVol == null && !unusualCall && !unusualPut && (
          <span style={{ color: 'var(--text-muted)' }}>Options whale activity</span>
        )}
      </div>
    </div>
  );
}
