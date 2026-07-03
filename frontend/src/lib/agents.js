/**
 * Agent definitions for the USA Swing 42-Agent Pipeline
 * Mirrors SPEC.md Section 12.1 (Agent ID Reference Table)
 *
 * Categories:
 * Direction        — Agents 1-6
 * News & Macro     — Agents 7-14
 * Institutional    — Agents 15-20
 * Strength         — Agents 21-26
 * Exit & Reversal  — Agents 27-29
 * Prediction Layer — Agents 30-33
 * Additional       — Agent 34
 * Commodity        — Agents 35-42
 */

import {
  Activity, BarChart2, TrendingUp, Globe, Newspaper, Shield, Database,
  Cpu, Users, Layers, Target, Zap, Clock, BookOpen, Compass, Scale,
  Briefcase, Crosshair, Filter, Hash, Box, TrendingDown, Flame, Sigma,
  GitBranch, Eye,
} from 'lucide-react'

// ─── Category definitions ──────────────────────────────────────────────────
export const AGENT_LAYERS = [
  { id: 'direction',        label: 'Direction',          color: '#2A7A6F', agents: [1, 2, 3, 4, 5, 6] },
  { id: 'news_macro',        label: 'News & Macro',       color: '#4A7C8E', agents: [7, 8, 9, 10, 11, 12, 13, 14] },
  { id: 'institutional',     label: 'Institutional',      color: '#7A6E9A', agents: [15, 16, 17, 18, 19, 20] },
  { id: 'strength',          label: 'Strength',           color: '#00838F', agents: [21, 22, 23, 24, 25, 26] },
  { id: 'exit_reversal',      label: 'Exit & Reversal',    color: '#E65100', agents: [27, 28, 29] },
  { id: 'prediction_layer',  label: 'Prediction Layer',   color: '#B5451B', agents: [30, 31, 32, 33] },
  { id: 'additional',        label: 'Additional',         color: '#558B2F', agents: [34] },
  { id: 'commodity',         label: 'Commodity',          color: '#F57F17', agents: [35, 36, 37, 38, 39, 40, 41, 42] },
]

// ─── 42-agent definitions ───────────────────────────────────────────────────
const BASE_AGENTS = [
  // ── Direction (1-6) ────────────────────────────────────────────────────────
  { id: 1,  key: 'regime_detection',   label: 'Regime Detection',       layer: 'direction',        icon: Activity,    tier: 1, desc: 'Classifies regime: trending-up, trending-down, range-bound, volatile, transitional' },
  { id: 2,  key: 'trend_structure',    label: 'Trend Structure',        layer: 'direction',        icon: TrendingUp,  tier: 1, desc: 'EMA8/21/50/200 alignment, golden/death cross, trend slope' },
  { id: 3,  key: 'market_breadth',     label: 'Market Breadth',         layer: 'direction',        icon: Layers,      tier: 1, desc: '% of S&P 500 above 20/50/200-day MA, advance/decline ratio' },
  { id: 4,  key: 'market_momentum',    label: 'Market Momentum',        layer: 'direction',        icon: Zap,         tier: 1, desc: 'RSI, MACD, ROC, Stochastic composite momentum score' },
  { id: 5,  key: 'trend_following',    label: 'Trend Following',        layer: 'direction',        icon: TrendingUp,  tier: 1, desc: 'Donchian/Keltner breakouts, 52-week high/low proximity' },
  { id: 6,  key: 'hmm_market_state',   label: 'HMM Market State',       layer: 'direction',        icon: GitBranch,   tier: 2, desc: 'Hidden Markov Model bull/bear/sideways state probability' },

  // ── News & Macro (7-14) ────────────────────────────────────────────────────
  { id: 7,  key: 'news_analyst',       label: 'News Analyst',           layer: 'news_macro',       icon: Newspaper,   tier: 1, desc: 'VADER/TextBlob sentiment scoring of latest news articles' },
  { id: 8,  key: 'earnings_sentiment', label: 'Earnings Sentiment',     layer: 'news_macro',       icon: BookOpen,    tier: 1, desc: 'Days to earnings, surprise history, post-earnings drift' },
  { id: 9,  key: 'event_detection',    label: 'Event Detection',        layer: 'news_macro',       icon: Eye,         tier: 1, desc: 'High-impact macro event proximity (CPI/PPI/GDP/FOMC)' },
  { id: 10, key: 'macro_news_impact',  label: 'Macro News Impact',      layer: 'news_macro',       icon: Globe,       tier: 1, desc: 'NLP theme extraction and macro news impact scoring' },
  { id: 11, key: 'macro_analyst',      label: 'Macro Analyst',          layer: 'news_macro',       icon: Compass,     tier: 1, desc: 'Yield curve slope, CPI trend, unemployment, M2 growth' },
  { id: 12, key: 'federal_reserve',    label: 'Federal Reserve',        layer: 'news_macro',       icon: Briefcase,   tier: 1, desc: 'Fed funds rate, rate direction, FOMC sentiment (hawkish/dovish)' },
  { id: 13, key: 'global_liquidity',   label: 'Global Liquidity',       layer: 'news_macro',       icon: Database,    tier: 2, desc: 'Fed balance sheet trend, global M2 proxy, DXY liquidity impact' },
  { id: 14, key: 'dollar_strength',    label: 'Dollar Strength',        layer: 'news_macro',       icon: Hash,        tier: 1, desc: 'DXY trend, RSI, position vs 200-day EMA' },

  // ── Institutional (15-20) ──────────────────────────────────────────────────
  { id: 15, key: 'sector_rotation',    label: 'Sector Rotation',        layer: 'institutional',    icon: Shield,      tier: 1, desc: 'Relative sector ETF performance, leading/lagging classification' },
  { id: 16, key: 'dark_pool_flow',     label: 'Dark Pool Flow',         layer: 'institutional',    icon: Eye,         tier: 2, desc: 'FINRA ATS weekly aggregate accumulation/distribution (degraded MVP)' },
  { id: 17, key: '13f_accumulation',   label: '13F Institutional Accumulation', layer: 'institutional', icon: Briefcase, tier: 1, desc: 'SEC 13F position changes, net institutional accumulation' },
  { id: 18, key: 'whale_options_flow', label: 'Whale Options Flow',     layer: 'institutional',    icon: Target,      tier: 2, desc: 'Unusually large options transactions, whale bias score' },
  { id: 19, key: 'insider_transactions', label: 'Insider Transactions', layer: 'institutional',    icon: Users,       tier: 1, desc: 'SEC Form 4 insider buy/sell activity and net value' },
  { id: 20, key: 'etf_flow_intelligence', label: 'ETF Flow Intelligence', layer: 'institutional',  icon: TrendingUp,  tier: 1, desc: 'ETF creation/redemption flow momentum, sector ETF flows' },

  // ── Strength (21-26) ───────────────────────────────────────────────────────
  { id: 21, key: 'put_call_parity',    label: 'Put/Call Parity',        layer: 'strength',         icon: Scale,       tier: 1, desc: 'Put/call ratio by volume and OI, IV skew, sentiment score' },
  { id: 22, key: 'gamma_exposure',     label: 'Gamma Exposure',         layer: 'strength',         icon: Zap,         tier: 1, desc: 'Dealer GEX, call wall, put wall, zero gamma level' },
  { id: 23, key: 'factor_crowding',    label: 'Factor Crowding',        layer: 'strength',         icon: Crosshair,   tier: 2, desc: 'Factor exposure crowding score and unwind risk' },
  { id: 24, key: 'uncertainty',        label: 'Uncertainty',            layer: 'strength',         icon: Filter,      tier: 1, desc: 'Composite uncertainty from VIX, events, and earnings proximity' },
  { id: 25, key: 'relative_strength',  label: 'Relative Strength',      layer: 'strength',         icon: BarChart2,   tier: 1, desc: 'RS ratio vs SPY/sector over 20/60/120 days' },
  { id: 26, key: 'vix_structure',      label: 'VIX Structure',          layer: 'strength',         icon: Activity,    tier: 1, desc: 'VIX level zones, term structure, fear/complacency score' },

  // ── Exit & Reversal (27-29) ────────────────────────────────────────────────
  { id: 27, key: 'correlation_decay',  label: 'Correlation Decay',      layer: 'exit_reversal',     icon: TrendingDown, tier: 2, desc: 'Rolling vs baseline correlation decay (early reversal signal)' },
  { id: 28, key: 'cross_asset_correlation', label: 'Cross Asset Correlation', layer: 'exit_reversal', icon: GitBranch, tier: 1, desc: 'Equity-commodity-DXY-rates correlation matrix, risk-on/off' },
  { id: 29, key: 'market_leadership',  label: 'Market Leadership',      layer: 'exit_reversal',     icon: Compass,     tier: 1, desc: 'Sector and symbol leadership rank within market' },

  // ── Prediction Layer (30-33) ───────────────────────────────────────────────
  { id: 30, key: 'signal_aggregation', label: 'Signal Aggregation',     layer: 'prediction_layer',  icon: Layers,      tier: 1, desc: 'Aggregates all 41 agents into weighted signal matrix' },
  { id: 31, key: 'ensemble_model',     label: 'Ensemble Model',         layer: 'prediction_layer',  icon: Cpu,         tier: 1, desc: 'LightGBM/XGBoost/CatBoost/RF/ExtraTrees/LogReg ensemble per horizon' },
  { id: 32, key: 'confidence_scoring', label: 'Confidence Scoring',     layer: 'prediction_layer',  icon: Sigma,       tier: 1, desc: 'Calibrated confidence with consensus, VIX, and event adjustments' },
  { id: 33, key: 'final_prediction_engine', label: 'Final Prediction Engine', layer: 'prediction_layer', icon: Target, tier: 1, desc: 'Direction, confidence, risk score, and expected move per horizon' },

  // ── Additional (34) ────────────────────────────────────────────────────────
  { id: 34, key: 'oi_structure',       label: 'Options OI Structure',   layer: 'additional',        icon: Box,         tier: 1, desc: 'Full OI profile: max pain, call wall, put wall, dealer delta' },

  // ── Commodity (35-42) ──────────────────────────────────────────────────────
  { id: 35, key: 'crude_oil',          label: 'Crude Oil Intelligence', layer: 'commodity',         icon: Flame,       tier: 1, desc: 'EIA inventory change, WTI-Brent spread, OPEC signal' },
  { id: 36, key: 'gold_precious_metals', label: 'Gold & Precious Metals', layer: 'commodity',       icon: Box,         tier: 1, desc: 'Gold vs DXY/real rates relationship, safe-haven demand' },
  { id: 37, key: 'natural_gas',        label: 'Natural Gas Intelligence', layer: 'commodity',       icon: Flame,       tier: 1, desc: 'EIA storage change vs consensus, seasonal deviation' },
  { id: 38, key: 'silver',             label: 'Silver Intelligence',    layer: 'commodity',         icon: Box,         tier: 1, desc: 'Gold-silver ratio, industrial demand proxy' },
  { id: 39, key: 'copper',             label: 'Copper Intelligence',    layer: 'commodity',         icon: Box,         tier: 1, desc: '"Dr. Copper" leading economic indicator vs S&P 500' },
  { id: 40, key: 'commodity_momentum', label: 'Commodity Momentum',     layer: 'commodity',         icon: TrendingUp,  tier: 1, desc: 'Composite momentum across commodity agents 35-39' },
  { id: 41, key: 'commodity_sentiment', label: 'Commodity Sentiment',   layer: 'commodity',         icon: Newspaper,   tier: 2, desc: 'News sentiment filtered for commodity keywords' },
  { id: 42, key: 'commodity_flow_positioning', label: 'Commodity Flow & Positioning', layer: 'commodity', icon: Database, tier: 2, desc: 'Commodity ETF flows and net positioning trend' },
]

// ─── Export functions ────────────────────────────────────────────────────────
export function getAgents() {
  return BASE_AGENTS
}

export function getAgentsByLayer() {
  const result = {}
  AGENT_LAYERS.forEach(layer => {
    result[layer.id] = {
      ...layer,
      agents: BASE_AGENTS.filter(a => a.layer === layer.id),
    }
  })
  return result
}

export function getAgentByKey(key) {
  return BASE_AGENTS.find(a => a.key === key)
}

export function getAgentById(id) {
  return BASE_AGENTS.find(a => a.id === id)
}

export default BASE_AGENTS
