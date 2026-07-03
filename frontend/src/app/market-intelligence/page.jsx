'use client';
/**
 * File: frontend/src/app/market-intelligence/page.jsx
 * Market Intelligence — macro/regime analysis dashboard.
 * Wires Agents 1, 3, 13, 14, 15, 28, 29 to chart/widget components.
 */
import { useState } from 'react';
import MainLayout from '@/components/layout/MainLayout';
import { useMarketRegime } from '@/hooks/useMarketData';
import { useAgentResults } from '@/hooks/useAgents';
import MarketBreadthWidget from '@/components/dashboard/MarketBreadthWidget';
import MarketRegimeWidget from '@/components/dashboard/MarketRegimeWidget';
import SectorRotationChart from '@/components/charts/SectorRotationChart';
import BreadthHistoryChart from '@/components/charts/BreadthHistoryChart';
import RegimeTimelineChart from '@/components/charts/RegimeTimelineChart';
import CorrelationHeatmap from '@/components/charts/CorrelationHeatmap';
import DXYStrengthWidget from '@/components/dashboard/DXYStrengthWidget';
import SectorRotationWidget from '@/components/dashboard/SectorRotationWidget';
import { Globe } from 'lucide-react';

const PERIODS = ['7d', '30d', '90d', '180d', '1y'];

export default function MarketIntelligencePage() {
  const [period, setPeriod] = useState('30d');
  const { regime, loading: regimeLoading } = useMarketRegime();
  const { results: agentResults, loading: agentsLoading } = useAgentResults('SPY');

  const agentMap = {};
  (agentResults || []).forEach(a => { agentMap[a.agent_id] = a; });
  const agent3 = agentMap[3];   // Market Breadth
  const agent13 = agentMap[13]; // Global Liquidity
  const agent14 = agentMap[14]; // Dollar Strength
  const agent15 = agentMap[15]; // Sector Rotation
  const agent28 = agentMap[28]; // Cross-Asset Correlation
  const agent29 = agentMap[29]; // Market Leadership

  const breadthHistory = agent3?.supporting_data?.breadth_history || [];
  const regimeHistory = agentMap[1]?.supporting_data?.regime_history || [];
  const sectorData = agent15?.supporting_data?.sector_data || [];
  const correlationMatrix = agent28?.supporting_data?.correlation_matrix || {};
  const correlationAssets = agent28?.supporting_data?.assets || ['SPY', 'TLT', 'GLD', 'DXY', 'VIX'];

  return (
    <MainLayout>
      <div className="p-4 md:p-6 space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl flex items-center justify-center"
              style={{ background: 'rgba(42,122,111,0.12)' }}>
              <Globe size={20} color="#2A7A6F" />
            </div>
            <div>
              <h1 className="text-xl font-bold" style={{ color: 'var(--text-primary)' }}>Market Intelligence</h1>
              <p className="text-xs" style={{ color: 'var(--text-muted)' }}>
                Macro regime, breadth, sector rotation, cross-asset correlations
              </p>
            </div>
          </div>
          <div className="flex gap-1.5">
            {PERIODS.map(p => (
              <button
                key={p}
                onClick={() => setPeriod(p)}
                className="px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors"
                style={{
                  background: period === p ? '#2A7A6F' : 'var(--bg-card)',
                  color: period === p ? '#fff' : 'var(--text-secondary)',
                  border: '1px solid var(--border)',
                }}
              >{p}</button>
            ))}
          </div>
        </div>

        {/* Top Row — Regime + Breadth + DXY */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <MarketRegimeWidget regime={regime} />
          <MarketBreadthWidget
            breadthScore={agent3?.score}
            pctAbove20d={agent3?.supporting_data?.pct_above_20d}
            pctAbove50d={agent3?.supporting_data?.pct_above_50d}
            pctAbove200d={agent3?.supporting_data?.pct_above_200d}
          />
          <DXYStrengthWidget
            dxySignal={agent14?.signal}
            dxyPrice={agent14?.supporting_data?.dxy_price}
            dxyRoc20={agent14?.supporting_data?.dxy_roc20}
            dxyRsi={agent14?.supporting_data?.dxy_rsi}
            dxyTrend={agent14?.supporting_data?.dxy_trend}
            dollarStrengthScore={agent14?.supporting_data?.dollar_strength_score}
          />
        </div>

        {/* Breadth History */}
        <div className="rounded-xl border p-5" style={{ background: 'var(--bg-card)', borderColor: 'var(--border)' }}>
          <h2 className="text-sm font-semibold mb-3" style={{ color: 'var(--text-muted)' }}>MARKET BREADTH HISTORY</h2>
          <BreadthHistoryChart breadthHistory={breadthHistory} period={period} />
        </div>

        {/* Regime Timeline */}
        <div className="rounded-xl border p-5" style={{ background: 'var(--bg-card)', borderColor: 'var(--border)' }}>
          <h2 className="text-sm font-semibold mb-3" style={{ color: 'var(--text-muted)' }}>MARKET REGIME TIMELINE</h2>
          <RegimeTimelineChart regimeHistory={regimeHistory} />
        </div>

        {/* Sector Rotation + Correlations */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <div className="rounded-xl border p-5" style={{ background: 'var(--bg-card)', borderColor: 'var(--border)' }}>
            <h2 className="text-sm font-semibold mb-3" style={{ color: 'var(--text-muted)' }}>SECTOR ROTATION ({period})</h2>
            <SectorRotationChart sectorData={sectorData} period={period} />
          </div>
          <div className="rounded-xl border p-5" style={{ background: 'var(--bg-card)', borderColor: 'var(--border)' }}>
            <h2 className="text-sm font-semibold mb-3" style={{ color: 'var(--text-muted)' }}>CROSS-ASSET CORRELATIONS</h2>
            <CorrelationHeatmap correlationMatrix={correlationMatrix} assets={correlationAssets} />
          </div>
        </div>

        {/* Sector Rotation Summary + Market Leadership */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <SectorRotationWidget agent15Data={agent15?.supporting_data} />
          <div className="rounded-xl border p-4" style={{ background: 'var(--bg-card)', borderColor: 'var(--border)' }}>
            <h2 className="text-xs font-semibold uppercase tracking-wider mb-3" style={{ color: 'var(--text-muted)' }}>
              Market Leadership
            </h2>
            {agent29 ? (
              <>
                <div className={`text-xl font-bold ${agent29.signal === 'Bullish' ? 'text-green-400' : agent29.signal === 'Bearish' ? 'text-red-400' : 'text-yellow-400'}`}>
                  {agent29.signal}
                </div>
                <p className="text-xs mt-1" style={{ color: 'var(--text-muted)' }}>
                  {agent29.reasoning || 'Breadth participation quality assessment'}
                </p>
                {agent29.supporting_data?.leadership_score != null && (
                  <p className="text-xs mt-2" style={{ color: 'var(--text-secondary)' }}>
                    Leadership Score: <span className="font-semibold">{agent29.supporting_data.leadership_score.toFixed(0)}</span>
                  </p>
                )}
              </>
            ) : (
              <p className="text-xs" style={{ color: 'var(--text-muted)' }}>
                {agentsLoading ? 'Loading…' : 'Generate a prediction for SPY to populate leadership data'}
              </p>
            )}
          </div>
        </div>
      </div>
    </MainLayout>
  );
}
