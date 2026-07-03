/**
 * File: frontend/src/components/charts/PriceChart.jsx
 * OHLCV price chart with volume bars and SMA overlays.
 *
 * Props: bars [{date,open,high,low,close,volume}], symbol, overlays {sma20,sma50,sma200}, markers
 */
'use client';
import { useMemo } from 'react';
import { ComposedChart, Line, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, ReferenceDot, CartesianGrid } from 'recharts';

function sma(data, period, key = 'close') {
  return data.map((d, i) => {
    if (i < period - 1) return null;
    const slice = data.slice(i - period + 1, i + 1);
    return slice.reduce((sum, b) => sum + (b[key] || 0), 0) / period;
  });
}

export default function PriceChart({ bars = [], symbol, overlays = { sma20: true, sma50: true, sma200: false }, markers = [] }) {
  const data = useMemo(() => {
    if (!bars || bars.length === 0) return [];
    const sma20 = overlays.sma20 ? sma(bars, 20) : [];
    const sma50 = overlays.sma50 ? sma(bars, 50) : [];
    const sma200 = overlays.sma200 ? sma(bars, 200) : [];
    return bars.map((b, i) => ({
      ...b,
      dateLabel: b.date ? new Date(b.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }) : '',
      sma20: sma20[i], sma50: sma50[i], sma200: sma200[i],
    }));
  }, [bars, overlays]);

  if (!bars || bars.length === 0) {
    return (
      <div className="rounded-xl border p-8 text-center" style={{ background: 'var(--bg-card)', borderColor: 'var(--border)', color: 'var(--text-muted)' }}>
        <p className="text-sm">No price data available{symbol ? ` for ${symbol}` : ''}</p>
      </div>
    );
  }

  return (
    <div className="rounded-xl border p-4" style={{ background: 'var(--bg-card)', borderColor: 'var(--border)' }}>
      {symbol && (
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-sm font-semibold" style={{ color: 'var(--text-primary)' }}>{symbol} Price</h3>
          <div className="flex gap-3 text-xs">
            {overlays.sma20 && <span className="flex items-center gap-1" style={{color:'var(--text-muted)'}}><span className="w-2 h-2 rounded-full" style={{ background: '#3b82f6' }} />SMA20</span>}
            {overlays.sma50 && <span className="flex items-center gap-1" style={{color:'var(--text-muted)'}}><span className="w-2 h-2 rounded-full" style={{ background: '#f59e0b' }} />SMA50</span>}
            {overlays.sma200 && <span className="flex items-center gap-1" style={{color:'var(--text-muted)'}}><span className="w-2 h-2 rounded-full" style={{ background: '#a855f7' }} />SMA200</span>}
          </div>
        </div>
      )}
      <ResponsiveContainer width="100%" height={320}>
        <ComposedChart data={data} margin={{ top: 5, right: 5, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" opacity={0.3} vertical={false} />
          <XAxis dataKey="dateLabel" tick={{ fill: 'var(--text-muted)', fontSize: 10 }} axisLine={false} tickLine={false} minTickGap={30} />
          <YAxis yAxisId="price" domain={['auto', 'auto']} tick={{ fill: 'var(--text-muted)', fontSize: 10 }} axisLine={false} tickLine={false} />
          <YAxis yAxisId="volume" orientation="right" tick={false} axisLine={false} tickLine={false} domain={[0, (max) => max * 4]} />
          <Tooltip contentStyle={{ background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 8, fontSize: 12 }}
            formatter={(v, name) => name === 'volume' ? [v?.toLocaleString(), 'Volume'] : [typeof v === 'number' ? `$${v.toFixed(2)}` : v, name]} />
          <Bar yAxisId="volume" dataKey="volume" fill="var(--border)" opacity={0.4} barSize={3} />
          <Line yAxisId="price" type="monotone" dataKey="close" stroke="#2A7A6F" strokeWidth={1.5} dot={false} name="Close" />
          {overlays.sma20 && <Line yAxisId="price" type="monotone" dataKey="sma20" stroke="#3b82f6" strokeWidth={1} dot={false} name="SMA20" />}
          {overlays.sma50 && <Line yAxisId="price" type="monotone" dataKey="sma50" stroke="#f59e0b" strokeWidth={1} dot={false} name="SMA50" />}
          {overlays.sma200 && <Line yAxisId="price" type="monotone" dataKey="sma200" stroke="#a855f7" strokeWidth={1} dot={false} name="SMA200" />}
          {markers.map((m, i) => {
            const point = data.find(d => d.date === m.date);
            if (!point) return null;
            return <ReferenceDot key={i} yAxisId="price" x={point.dateLabel} y={point.close} r={5}
              fill={m.type === 'entry' ? '#22c55e' : '#ef4444'} stroke="#fff" strokeWidth={1} />;
          })}
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
}
