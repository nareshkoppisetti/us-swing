/**
 * File: frontend/src/components/charts/OIHeatmap.jsx
 * Open interest heatmap by strike and expiration.
 * Props: oiData [{strike, expiration, call_oi, put_oi}]
 */
'use client';
import { useMemo } from 'react';

export default function OIHeatmap({ oiData = [] }) {
  const { strikes, expirations, maxOI } = useMemo(() => {
    if (!oiData || oiData.length === 0) return { strikes: [], expirations: [], maxOI: 0 };
    const strikeSet = [...new Set(oiData.map(d => d.strike))].sort((a, b) => a - b);
    const expSet = [...new Set(oiData.map(d => d.expiration))].sort();
    const max = Math.max(...oiData.map(d => (d.call_oi || 0) + (d.put_oi || 0)));
    return { strikes: strikeSet, expirations: expSet, maxOI: max };
  }, [oiData]);

  if (!oiData || oiData.length === 0) {
    return (
      <div className="text-center py-10 text-sm" style={{ color: 'var(--text-muted)' }}>
        No open interest data available
      </div>
    );
  }

  const lookup = {};
  oiData.forEach(d => { lookup[`${d.strike}-${d.expiration}`] = d; });

  return (
    <div className="overflow-x-auto">
      <table className="border-collapse text-xs">
        <thead>
          <tr>
            <th className="p-1.5 text-left" style={{ color: 'var(--text-muted)' }}>Strike</th>
            {expirations.map(e => (
              <th key={e} className="p-1.5 font-mono text-center" style={{ color: 'var(--text-muted)' }}>{e}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {strikes.map(s => (
            <tr key={s}>
              <td className="p-1.5 font-mono font-semibold" style={{ color: 'var(--text-primary)' }}>{s}</td>
              {expirations.map(e => {
                const cell = lookup[`${s}-${e}`];
                const total = cell ? (cell.call_oi || 0) + (cell.put_oi || 0) : 0;
                const intensity = maxOI > 0 ? total / maxOI : 0;
                const callDominant = cell && (cell.call_oi || 0) >= (cell.put_oi || 0);
                return (
                  <td key={e} className="p-0">
                    <div
                      className="w-10 h-8 m-0.5 rounded flex items-center justify-center text-[10px]"
                      style={{
                        background: callDominant
                          ? `rgba(34,197,94,${0.15 + intensity * 0.6})`
                          : `rgba(239,68,68,${0.15 + intensity * 0.6})`,
                        color: 'var(--text-primary)',
                      }}
                      title={cell ? `Calls: ${cell.call_oi} / Puts: ${cell.put_oi}` : '—'}
                    >
                      {total > 0 ? (total / 1000).toFixed(1) + 'k' : ''}
                    </div>
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
