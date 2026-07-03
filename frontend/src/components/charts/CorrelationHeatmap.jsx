/**
 * File: frontend/src/components/charts/CorrelationHeatmap.jsx
 * Cross-asset correlation matrix heatmap (equity/bond/gold/DXY etc.)
 * Props: correlationMatrix { [asset]: { [asset]: corrValue } }, assets [string]
 */
'use client';

function corrColor(v) {
  if (v == null) return 'var(--bg-secondary)';
  // -1 (red) -> 0 (neutral) -> +1 (green)
  if (v >= 0) {
    const intensity = Math.min(1, v);
    return `rgba(34, 197, 94, ${0.15 + intensity * 0.65})`;
  }
  const intensity = Math.min(1, Math.abs(v));
  return `rgba(239, 68, 68, ${0.15 + intensity * 0.65})`;
}

export default function CorrelationHeatmap({ correlationMatrix = {}, assets = [] }) {
  if (!assets || assets.length === 0) {
    return (
      <div className="text-center py-10 text-sm" style={{ color: 'var(--text-muted)' }}>
        No correlation data available
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="border-collapse w-full text-xs">
        <thead>
          <tr>
            <th className="p-1.5" />
            {assets.map(a => (
              <th key={a} className="p-1.5 font-mono font-semibold text-center" style={{ color: 'var(--text-muted)' }}>{a}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {assets.map(rowAsset => (
            <tr key={rowAsset}>
              <td className="p-1.5 font-mono font-semibold" style={{ color: 'var(--text-muted)' }}>{rowAsset}</td>
              {assets.map(colAsset => {
                const v = correlationMatrix?.[rowAsset]?.[colAsset];
                return (
                  <td key={colAsset} className="p-0">
                    <div
                      className="w-12 h-12 flex items-center justify-center text-xs font-semibold m-0.5 rounded"
                      style={{ background: corrColor(v), color: 'var(--text-primary)' }}
                      title={`${rowAsset} vs ${colAsset}: ${v != null ? v.toFixed(2) : 'N/A'}`}
                    >
                      {v != null ? v.toFixed(2) : '—'}
                    </div>
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
      <div className="flex items-center gap-4 mt-3 text-xs" style={{ color: 'var(--text-muted)' }}>
        <span className="flex items-center gap-1.5">
          <span className="w-3 h-3 rounded" style={{ background: 'rgba(239,68,68,0.6)' }} />Negative
        </span>
        <span className="flex items-center gap-1.5">
          <span className="w-3 h-3 rounded" style={{ background: 'rgba(34,197,94,0.6)' }} />Positive
        </span>
      </div>
    </div>
  );
}
