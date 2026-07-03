'use client';
import { TrendingUp, TrendingDown } from 'lucide-react';

/**
 * Wired to Agent 14 (Dollar Strength) actual output:
 *   supporting_data: { dxy_price, dxy_sma20, dxy_roc20, dxy_rsi, dxy_trend,
 *                      dollar_strength_score, equity_impact_score }
 */
export default function DXYStrengthWidget({ dxySignal, dxyPrice, dxyRoc20, dollarStrengthScore, dxyRsi, dxyTrend }) {
  const up = dxySignal === 'Bullish';
  return (
    <div className="rounded-xl border p-4 h-full" style={{ background: 'var(--bg-card)', borderColor: 'var(--border)' }}>
      <div className="flex items-center justify-between mb-3">
        <span className="text-xs font-semibold uppercase tracking-wider" style={{ color: 'var(--text-muted)' }}>DXY Strength</span>
        {up ? <TrendingUp size={14} className="text-red-400" /> : <TrendingDown size={14} className="text-green-400" />}
      </div>
      <div className={`text-lg font-bold ${up ? 'text-red-400' : 'text-green-400'}`}>{dxySignal || 'Neutral'}</div>
      <div className="mt-2 space-y-1 text-xs">
        {dxyPrice != null && (
          <div className="flex justify-between">
            <span style={{ color: 'var(--text-muted)' }}>DXY Price</span>
            <span style={{ color: 'var(--text-secondary)', fontWeight: 600 }}>{dxyPrice.toFixed(2)}</span>
          </div>
        )}
        {dxyTrend && (
          <div className="flex justify-between">
            <span style={{ color: 'var(--text-muted)' }}>Trend</span>
            <span className={dxyTrend === 'Rising' ? 'text-red-400' : dxyTrend === 'Falling' ? 'text-green-400' : 'text-yellow-400'}
              style={{ fontWeight: 600 }}>{dxyTrend}</span>
          </div>
        )}
        {dxyRsi != null && (
          <div className="flex justify-between">
            <span style={{ color: 'var(--text-muted)' }}>RSI(14)</span>
            <span style={{ color: 'var(--text-secondary)', fontWeight: 600 }}>{dxyRsi.toFixed(0)}</span>
          </div>
        )}
        {dxyRoc20 != null && (
          <div className="flex justify-between">
            <span style={{ color: 'var(--text-muted)' }}>20d ROC</span>
            <span className={dxyRoc20 >= 0 ? 'text-red-400' : 'text-green-400'} style={{ fontWeight: 600 }}>
              {dxyRoc20 >= 0 ? '+' : ''}{dxyRoc20.toFixed(1)}%
            </span>
          </div>
        )}
      </div>
      <div className="text-xs mt-2" style={{ color: 'var(--text-muted)' }}>
        {up ? '⚠ Strong USD = headwind for equities/commodities' : '✓ Weak USD = tailwind for risk assets'}
      </div>
    </div>
  );
}
