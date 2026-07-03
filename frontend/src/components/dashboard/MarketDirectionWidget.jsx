'use client';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { formatPct } from '@/lib/utils';

export default function MarketDirectionWidget({ prediction }) {
  const dir = prediction?.direction || 'Neutral';
  const conf = prediction?.confidence;
  const move = prediction?.expected_move_pct;
  const isUp = dir === 'Bullish';
  const isDown = dir === 'Bearish';

  return (
    <div className="rounded-xl border p-4 h-full" style={{ background: 'var(--bg-card)', borderColor: 'var(--border)' }}>
      <div className="flex items-center justify-between mb-3">
        <span className="text-xs font-semibold uppercase tracking-wider" style={{ color: 'var(--text-muted)' }}>SPY Direction (5D)</span>
        {isUp ? <TrendingUp size={14} className="text-green-400" /> : isDown ? <TrendingDown size={14} className="text-red-400" /> : <Minus size={14} className="text-yellow-400" />}
      </div>
      <div className={`text-2xl font-black ${isUp ? 'text-green-400' : isDown ? 'text-red-400' : 'text-yellow-400'}`}>
        {dir}
      </div>
      <div className="mt-2 flex items-center gap-3 text-sm">
        {conf != null && <span style={{ color: 'var(--text-muted)' }}>Conf: <span className="font-semibold" style={{ color: 'var(--text-primary)' }}>{conf.toFixed(0)}%</span></span>}
        {move != null && <span className={move >= 0 ? 'text-green-400' : 'text-red-400'}>{formatPct(move)}</span>}
      </div>
    </div>
  );
}
