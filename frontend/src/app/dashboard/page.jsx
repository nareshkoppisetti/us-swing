/**
 * File: frontend/src/app/dashboard/page.jsx
 * Main dashboard — wires all 20 widgets with real backend data.
 *
 * SPEC Section 7.2, BUILD_PLAN Phase 13.4
 */
'use client';
import { useState, useEffect, useMemo } from 'react';
import MainLayout from '@/components/layout/MainLayout';
import { useMarketRegime, useVIX } from '@/hooks/useMarketData';
import { usePredictions, useWatchlistSignals, useGeneratePrediction } from '@/hooks/usePredictions';
import { useAgentDefinitions, useAgentResults } from '@/hooks/useAgents';
import { useAlerts } from '@/hooks/useAlerts';
import { useAccuracy } from '@/hooks/usePerformance';
import { useEtfFlows } from '@/hooks/useInstitutional';
import { useWebSocket } from '@/hooks/useWebSocket';

import MarketRegimeWidget from '@/components/dashboard/MarketRegimeWidget';
import MarketDirectionWidget from '@/components/dashboard/MarketDirectionWidget';
import ConfidenceScoreWidget from '@/components/dashboard/ConfidenceScoreWidget';
import RiskScoreWidget from '@/components/dashboard/RiskScoreWidget';
import ExpectedMoveWidget from '@/components/dashboard/ExpectedMoveWidget';
import MarketBreadthWidget from '@/components/dashboard/MarketBreadthWidget';
import MomentumScoreWidget from '@/components/dashboard/MomentumScoreWidget';
import VIXStructureWidget from '@/components/dashboard/VIXStructureWidget';
import DXYStrengthWidget from '@/components/dashboard/DXYStrengthWidget';
import SectorRotationWidget from '@/components/dashboard/SectorRotationWidget';
import InstitutionalFlowSummary from '@/components/dashboard/InstitutionalFlowSummary';
import ETFFlowSummary from '@/components/dashboard/ETFFlowSummary';
import WhaleFlowSummary from '@/components/dashboard/WhaleFlowSummary';
import BullishDriversWidget from '@/components/dashboard/BullishDriversWidget';
import BearishDriversWidget from '@/components/dashboard/BearishDriversWidget';
import AgentConsensusWidget from '@/components/dashboard/AgentConsensusWidget';
import PredictionTimeline from '@/components/dashboard/PredictionTimeline';
import HistoricalAccuracyWidget from '@/components/dashboard/HistoricalAccuracyWidget';
import ActiveAlertsWidget from '@/components/dashboard/ActiveAlertsWidget';
import MajorRisksWidget from '@/components/dashboard/MajorRisksWidget';
import GlobalSearchBar from '@/components/search/GlobalSearchBar';
import { Search, RefreshCw } from 'lucide-react';

/**
 * Major US indices available from the quick-select strip. These use the
 * tracking ETF as the underlying symbol (SPY for S&P 500, etc.) because
 * that's what the prediction/options/agent pipeline is built around —
 * raw index tickers like ^GSPC have no options chain to analyze.
 */
const INDEX_OPTIONS = [
  { symbol: 'SPY', label: 'S&P 500' },
  { symbol: 'QQQ', label: 'Nasdaq 100' },
  { symbol: 'DIA', label: 'Dow Jones' },
  { symbol: 'IWM', label: 'Russell 2000' },
];

/** Live clock — re-renders every second, always shows the viewer's own local time/timezone. */
function LiveClock() {
  const [now, setNow] = useState(new Date());
  useEffect(() => {
    const id = setInterval(() => setNow(new Date()), 1000);
    return () => clearInterval(id);
  }, []);

  const tz = useMemo(() => {
    try { return Intl.DateTimeFormat().resolvedOptions().timeZone; } catch { return ''; }
  }, []);

  const dateStr = now.toLocaleDateString(undefined, {
    weekday: 'short', year: 'numeric', month: 'short', day: 'numeric',
  });
  // timeZoneName shows the local zone abbreviation (e.g. IST, EDT) so it's
  // clear this is the viewer's own location time, not a fixed server time.
  const timeStr = now.toLocaleTimeString(undefined, { hour12: true, timeZoneName: 'short' });

  return (
    <p className="text-sm" style={{ color: 'var(--text-muted)' }} title={tz}>
      {dateStr} · <span className="font-mono">{timeStr}</span>
    </p>
  );
}

function LoadingPlaceholder() {
  return (
    <div className="rounded-xl border animate-pulse h-28" style={{ background: 'var(--bg-card)', borderColor: 'var(--border)' }} />
  );
}

function SectionHeader({ title, action }) {
  return (
    <div className="flex items-center justify-between mb-3">
      <h2 className="text-xs font-bold uppercase tracking-widest" style={{ color: 'var(--text-muted)' }}>{title}</h2>
      {action}
    </div>
  );
}

export default function DashboardPage() {
  const [searchOpen, setSearchOpen] = useState(false);
  // Which index/symbol all the widgets below are showing. Defaults to
  // SPY (S&P 500) so it's obvious what "the market" refers to on first load.
  // Selecting an index only changes *what will be generated next* — it does
  // NOT trigger a prediction run by itself. That only happens when the user
  // clicks "Generate Prediction" below.
  const [symbol, setSymbol] = useState('SPY');

  const { regime, loading: regimeLoading } = useMarketRegime();
  const { vix } = useVIX();
  const { predictions, loading: predsLoading, refetch: refetchPredictions } = usePredictions({ symbol, page_size: 10 });
  const { results: agentOutputs } = useAgentResults(symbol);
  const { alerts } = useAlerts({ status: 'active', page_size: 10 });
  const { accuracy } = useAccuracy({ rolling_days: 30 });
  const { flows } = useEtfFlows(symbol);
  const { subscribe } = useWebSocket();
  const { generate, generating } = useGeneratePrediction();

  // Live WebSocket updates
  const [liveAlerts, setLiveAlerts] = useState([]);
  useEffect(() => {
    const unsub = subscribe('alerts', (data) => {
      setLiveAlerts(prev => [data, ...prev].slice(0, 20));
    });
    return unsub;
  }, [subscribe]);

  // Ctrl+K keyboard shortcut
  useEffect(() => {
    const handler = () => setSearchOpen(true);
    document.addEventListener('open-search', handler);
    const keyHandler = (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') { e.preventDefault(); setSearchOpen(true); }
    };
    document.addEventListener('keydown', keyHandler);
    return () => {
      document.removeEventListener('open-search', handler);
      document.removeEventListener('keydown', keyHandler);
    };
  }, []);

  // Parse agent outputs for specific agents
  const agentMap = {};
  (agentOutputs || []).forEach(a => { agentMap[a.agent_id] = a; });

  const symbolPred5d = (predictions || []).find(p => p.horizon_days === 5);
  const allAlerts = [...liveAlerts, ...(alerts || [])];

  // Prediction generation is manual-only: the user picks an index above,
  // then clicks "Generate Prediction" below. Nothing runs automatically on
  // page load or on index switch — this handler is the only place `generate`
  // is ever called from this page.
  const handleGeneratePrediction = () => {
    if (generating) return;
    generate(symbol).then(() => refetchPredictions()).catch(() => {});
  };

  // Agent 30 signal aggregation data
  const agent30 = agentMap[30];
  const agent26 = agentMap[26]; // VIX
  const agent14 = agentMap[14]; // DXY
  const agent3 = agentMap[3];   // Breadth
  const agent4 = agentMap[4];   // Momentum
  const agent15 = agentMap[15]; // Sector Rotation
  const agent18 = agentMap[18]; // Whale Flow
  const agent9 = agentMap[9];   // Event Detection
  const agent24 = agentMap[24]; // Uncertainty

  // Compute consensus counts from agent outputs
  const bullCount = agentOutputs.filter(a => a.signal === 'Bullish').length;
  const bearCount = agentOutputs.filter(a => a.signal === 'Bearish').length;
  const neutralCount = agentOutputs.filter(a => a.signal === 'Neutral').length;

  // Extract bullish/bearish factors from predictions and agents
  const bullishFactors = symbolPred5d?.bullish_factors ||
    agentOutputs.flatMap(a => a.bullish_factors || []).slice(0, 5);
  const bearishFactors = symbolPred5d?.bearish_factors ||
    agentOutputs.flatMap(a => a.bearish_factors || []).slice(0, 5);

  const currentIndex = INDEX_OPTIONS.find(i => i.symbol === symbol);

  return (
    <MainLayout>
      <div className="p-4 md:p-6 space-y-6">

        {/* Page title */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <div>
            <h1 className="text-xl font-bold" style={{ color: 'var(--text-primary)' }}>Market Dashboard</h1>
            <p className="text-sm" style={{ color: 'var(--text-muted)' }}>
              Showing: <span className="font-semibold" style={{ color: '#2A7A6F' }}>
                {currentIndex ? `${currentIndex.label} (${currentIndex.symbol})` : symbol}
              </span>
              {generating && <span className="ml-2 inline-flex items-center gap-1" style={{ color: 'var(--text-muted)' }}>
                <RefreshCw size={11} className="animate-spin" /> generating prediction…
              </span>}
              {!generating && !predsLoading && !symbolPred5d && (
                <span className="ml-2" style={{ color: 'var(--text-muted)' }}>
                  · no prediction yet — click Generate Prediction
                </span>
              )}
            </p>
          </div>
          <LiveClock />
        </div>

        {/* Full-width symbol search — the one search bar in the app */}
        <button
          onClick={() => setSearchOpen(true)}
          className="w-full flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm border transition-colors hover:bg-white/5"
          style={{ background: 'var(--bg-card)', borderColor: 'var(--border)', color: 'var(--text-muted)' }}
        >
          <Search size={15} />
          <span>Search any symbol… (Ctrl+K)</span>
        </button>

        {/* Quick-select — major US indices. Click one to load its data + predictions below. */}
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-xs font-semibold uppercase tracking-wider mr-1" style={{ color: 'var(--text-muted)' }}>
            Indices
          </span>
          {INDEX_OPTIONS.map(opt => {
            const active = opt.symbol === symbol;
            return (
              <button
                key={opt.symbol}
                onClick={() => setSymbol(opt.symbol)}
                className="px-3 py-1.5 rounded-lg text-xs font-medium border transition-colors"
                style={{
                  background: active ? '#2A7A6F' : 'var(--bg-card)',
                  borderColor: active ? '#2A7A6F' : 'var(--border)',
                  color: active ? '#fff' : 'var(--text-secondary)',
                }}
              >
                {opt.label} <span className="opacity-70">· {opt.symbol}</span>
              </button>
            );
          })}

          {/* Manual, on-demand trigger — this is the ONLY thing that starts a
              prediction run. It always acts on whichever index is selected
              above at the moment it's clicked. */}
          <button
            onClick={handleGeneratePrediction}
            disabled={generating}
            className="ml-auto px-4 py-1.5 rounded-lg text-xs font-semibold border transition-colors disabled:opacity-60 flex items-center gap-1.5"
            style={{ background: '#2A7A6F', borderColor: '#2A7A6F', color: '#fff' }}
          >
            <RefreshCw size={12} className={generating ? 'animate-spin' : ''} />
            {generating ? 'Generating…' : `Generate Prediction · ${symbol}`}
          </button>
        </div>

        {/* === ROW 1 — Core market state (4 cols) === */}
        <div>
          <SectionHeader title="Market State" />
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
            {regimeLoading ? <LoadingPlaceholder /> : <MarketRegimeWidget regime={regime} />}
            {predsLoading ? <LoadingPlaceholder /> : (
              <MarketDirectionWidget
                prediction={symbolPred5d}
              />
            )}
            <ConfidenceScoreWidget confidence={symbolPred5d?.confidence} />
            <RiskScoreWidget riskScore={symbolPred5d?.risk_score} />
          </div>
        </div>

        {/* === ROW 2 — Technical indicators (4 cols) === */}
        <div>
          <SectionHeader title="Technical Indicators" />
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
            <MarketBreadthWidget
              breadthScore={agent3?.score}
              pctAbove20d={agent3?.supporting_data?.pct_above_20d}
              pctAbove50d={agent3?.supporting_data?.pct_above_50d}
              pctAbove200d={agent3?.supporting_data?.pct_above_200d}
            />
            <MomentumScoreWidget
              momentumScore={agent4?.score}
              rsi={agent4?.supporting_data?.rsi_14}
              macdSignal={agent4?.supporting_data?.macd_signal}
            />
            <VIXStructureWidget
              vixLevel={vix?.vix ?? agent26?.supporting_data?.vix}
              vixStructure={vix?.term_structure ?? agent26?.supporting_data?.term_structure}
              score={agent26?.score}
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
        </div>

        {/* === ROW 3 — Options & Move (3 cols) === */}
        <div>
          <SectionHeader title="Options & Move" />
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            <ExpectedMoveWidget expectedMove={symbolPred5d?.expected_move_pct} horizon={5} />
            <AgentConsensusWidget
              compositeScore={agent30?.supporting_data?.composite_score}
              bullCount={bullCount}
              bearCount={bearCount}
              neutralCount={neutralCount}
            />
            <WhaleFlowSummary whaleData={agent18?.supporting_data} />
          </div>
        </div>

        {/* === ROW 4 — Flows & Sector (3 cols) === */}
        <div>
          <SectionHeader title="Flows & Sectors" />
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            <InstitutionalFlowSummary flows={flows} />
            <ETFFlowSummary etfFlows={agentMap[20]?.supporting_data} />
            <SectorRotationWidget agent15Data={agent15?.supporting_data} />
          </div>
        </div>

        {/* === ROW 5 — Drivers & Risks (3 cols) === */}
        <div>
          <SectionHeader title="Key Drivers" />
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            <BullishDriversWidget factors={bullishFactors} />
            <BearishDriversWidget factors={bearishFactors} />
            <MajorRisksWidget
              uncertaintyScore={agent24?.score}
              eventRiskData={agent9?.supporting_data}
            />
          </div>
        </div>

        {/* === ROW 6 — History & Alerts (3 cols) === */}
        <div>
          <SectionHeader title="Performance & Alerts" />
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            <PredictionTimeline predictions={predictions} />
            <HistoricalAccuracyWidget accuracy={accuracy} />
            <ActiveAlertsWidget alerts={allAlerts} />
          </div>
        </div>

      </div>

      {searchOpen && <GlobalSearchBar onClose={() => setSearchOpen(false)} />}
    </MainLayout>
  );
}
