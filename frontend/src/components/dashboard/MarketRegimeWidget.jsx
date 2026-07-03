'use client';
import { Activity } from 'lucide-react';

/**
 * Wired to /market/regime endpoint which returns:
 *   { regime: string, score: float, source: "agent_1"|"computed"|"default" }
 *   regime is the raw signal string e.g. "Bullish", "Bearish", "Neutral"
 *   or regime label from Agent 1 e.g. "Trending-Up", "Range-Bound", etc.
 */
const REGIME_COLOR = {
  'Trending-Up': 'text-green-400',
  'Trending-Down': 'text-red-400',
  'Range-Bound': 'text-yellow-400',
  Volatile: 'text-orange-400',
  Transitional: 'text-blue-400',
  Bullish: 'text-green-400',
  Bearish: 'text-red-400',
  Neutral: 'text-gray-400',
  Trending: 'text-green-400',
  Unknown: 'text-gray-400',
};
const REGIME_BG = {
  'Trending-Up': 'bg-green-500/10 border-green-500/20',
  'Trending-Down': 'bg-red-500/10 border-red-500/20',
  'Range-Bound': 'bg-yellow-500/10 border-yellow-500/20',
  Volatile: 'bg-orange-500/10 border-orange-500/20',
  Transitional: 'bg-blue-500/10 border-blue-500/20',
  Bullish: 'bg-green-500/10 border-green-500/20',
  Bearish: 'bg-red-500/10 border-red-500/20',
  Neutral: 'bg-gray-500/10 border-gray-500/20',
  Trending: 'bg-green-500/10 border-green-500/20',
};

export default function MarketRegimeWidget({ regime }) {
  // regime endpoint returns { regime, score, source }
  const label  = regime?.regime || regime?.regime_label || 'Unknown';
  const score  = regime?.score;
  const source = regime?.source;

  return (
    <div className="rounded-xl border p-4 h-full" style={{ background: 'var(--bg-card)', borderColor: 'var(--border)' }}>
      <div className="flex items-center justify-between mb-3">
        <span className="text-xs font-semibold uppercase tracking-wider" style={{ color: 'var(--text-muted)' }}>Market Regime</span>
        <Activity size={14} style={{ color: 'var(--text-muted)' }} />
      </div>

      <div className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-bold border
        ${REGIME_BG[label] || 'bg-gray-500/10 border-gray-500/20'}`}>
        <span className={REGIME_COLOR[label] || 'text-gray-400'}>{label}</span>
      </div>

      <div className="mt-3 grid grid-cols-2 gap-2">
        {score != null && (
          <div>
            <div className="text-xs" style={{ color: 'var(--text-muted)' }}>Score</div>
            <div className="text-lg font-bold" style={{ color: 'var(--text-primary)' }}>{score.toFixed(0)}</div>
          </div>
        )}
        {source && (
          <div>
            <div className="text-xs" style={{ color: 'var(--text-muted)' }}>Source</div>
            <div className="text-xs font-semibold mt-0.5 capitalize" style={{ color: 'var(--text-secondary)' }}>
              {source.replace('_', ' ')}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
