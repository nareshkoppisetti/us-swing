# USA Swing — Institutional-Grade Market Intelligence & Swing Trading Prediction Platform
## Complete Software Requirements Specification (SRS) & System Design Specification (SDS)

**Version:** 1.0.0  
**Classification:** Production-Grade Specification  
**Document Status:** Authoritative Implementation Reference  

> **LLM Implementation Directive:** This document is the single source of truth for the USA Swing platform. Every architectural decision, data model, agent design, API contract, and deployment strategy defined herein must be implemented exactly as specified. No major architectural decisions are left open — this document is intentionally exhaustive so that implementation can begin immediately without ambiguity. Do not deviate from naming conventions, module structure, or data schemas without updating this specification.

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Business Objectives](#2-business-objectives)
3. [System Overview](#3-system-overview)
4. [Functional Requirements](#4-functional-requirements)
5. [Non-Functional Requirements](#5-non-functional-requirements)
6. [Technology Stack](#6-technology-stack)
7. [Frontend Architecture](#7-frontend-architecture)
8. [Admin Panel Architecture](#8-admin-panel-architecture)
9. [Backend Architecture](#9-backend-architecture)
10. [Database Architecture](#10-database-architecture)
11. [Market Data Architecture](#11-market-data-architecture)
12. [Agent Architecture (42 Agents)](#12-agent-architecture-42-agents)
13. [Prediction Engine Architecture](#13-prediction-engine-architecture)
14. [Explainability Engine & LLM Narrative System](#14-explainability-engine--llm-narrative-system)
15. [Machine Learning Architecture](#15-machine-learning-architecture)
16. [API Architecture](#16-api-architecture)
17. [Security Architecture](#17-security-architecture)
18. [Monitoring & Observability](#18-monitoring--observability)
19. [Deployment Architecture](#19-deployment-architecture)
20. [Cost Analysis](#20-cost-analysis)
21. [Risk Analysis](#21-risk-analysis)
22. [Scalability Strategy](#22-scalability-strategy)
23. [MVP Roadmap](#23-mvp-roadmap)
24. [Production Roadmap](#24-production-roadmap)
25. [Enterprise Roadmap](#25-enterprise-roadmap)
26. [Complete Folder Structure](#26-complete-folder-structure)
27. [Environment Configuration](#27-environment-configuration)

---

## 1. Executive Summary

### 1.1 Project Purpose

USA Swing is an **institutional-grade market intelligence and swing trading prediction platform** covering ALL US equity markets — individual stocks, ETFs, major indices, and commodities. It is not a retail signal-selling application. Every prediction is explainable, auditable, measurable, and supported by data, agent reasoning, institutional flow analysis, and historical validation.

### 1.2 Business Goals

- Provide institutional-quality market direction predictions for any searchable US-listed symbol or commodity
- Combine structured quantitative analysis (42 specialized AI agents) with machine learning ensemble models and LLM-powered natural-language explanations
- Answer four core questions for every prediction: **Where is it going? Why is it moving? How strong is the signal? When will the trend end?**
- Build a scalable, maintainable platform that evolves from MVP (single developer) to enterprise (thousands of users) without architectural rewrites

### 1.3 Vision

Build a platform comparable in concept to professional research and decision-support systems used by portfolio managers, quantitative researchers, proprietary trading firms, and hedge funds — but architected to start lean, use free data sources, and scale gracefully.

### 1.4 Scope

**In Scope:**
- All NYSE, NASDAQ, AMEX listed stocks
- All US ETFs (sector, index, commodity, bond)
- Primary Indices: SPX/SPY, NDX/QQQ, DJIA, Russell 2000/IWM
- Commodities: Crude Oil (CL/USO), Gold (GC/GLD), Natural Gas (NG/UNG), Silver (SI/SLV), Copper (HG/CPER), Wheat (ZW), Corn (ZC), Soybeans (ZS), all major commodity futures
- Symbol search with full analysis for any searched symbol
- Prediction horizons: 2D, 5D, 10D, 20D, 30D, 60D
- 42-agent analysis pipeline with full explainability
- LLM-generated analyst-grade explanation narratives per prediction

**Out of Scope (MVP):**
- International equities
- Forex (FX pairs)
- Fixed income (bonds) beyond ETF coverage
- Real-time tick data / HFT capabilities
- Order execution or brokerage integration

---

## 2. Business Objectives

### 2.1 Primary User Goals

| User Type | Primary Goal | Secondary Goal |
|-----------|-------------|----------------|
| Portfolio Manager | Identify high-conviction swing opportunities across all US assets | Monitor institutional flow alignment |
| Quantitative Analyst | Access explainable, auditable agent signals with raw data | Run backtests and validate prediction quality |
| Research Analyst | Understand market regime and macro drivers | Generate research-ready narrative explanations |
| Risk Manager | Identify trend exhaustion and reversal conditions | Monitor prediction confidence drift |
| Proprietary Trading Firm | High-confidence swing signals for any US symbol | Agent-level attribution and weight breakdown |
| Hedge Fund / Family Office | Broad market intelligence + sector rotation analysis | Historical prediction performance validation |
| Professional Swing Trader | Actionable predictions with clear entry rationale | News and event impact on predictions |

### 2.2 Business Success Metrics

- **Prediction Directional Accuracy:** ≥ 58% across all horizons (baseline target)
- **Agent Health:** ≥ 95% of 42 agents in healthy status at all times
- **Prediction Latency:** Full 42-agent pipeline execution ≤ 5 minutes per symbol
- **Explanation Generation:** ≥ 99% of predictions have an explanation (LLM or fallback)
- **Data Freshness:** Market data updated within 15 minutes of market close
- **System Uptime:** ≥ 99.5% during US market hours (9:30 AM – 4:00 PM ET)
- **API Response Time:** 95th percentile ≤ 800ms for prediction fetch endpoints

### 2.3 Key Performance Indicators (KPIs)

- Win Rate per prediction horizon (2D, 5D, 10D, 20D, 30D, 60D)
- Sharpe Ratio of prediction-implied returns
- Agent consensus rate (% of agents agreeing with final direction)
- Explanation quality score (LLM vs fallback ratio)
- Data source availability rate per source
- User search query volume per symbol

---

## 3. System Overview

### 3.1 Platform Overview

USA Swing is a **modular monolith** (MVP) structured around three main runtime layers:

1. **Data Ingestion Layer** — collects market data, news, economic data, institutional data, and commodity data from free APIs
2. **Intelligence Layer** — 42 specialized AI agents process collected data and produce scored, weighted signals
3. **Prediction Layer** — ML ensemble models aggregate agent outputs into directional predictions with confidence, risk, and LLM narrative explanations

### 3.2 Major Components

```
┌─────────────────────────────────────────────────────────────┐
│                        FRONTEND (Next.js)                    │
│  Dashboard | Predictions | Agent Analysis | Admin | Search   │
└─────────────────────────┬───────────────────────────────────┘
                          │ REST + WebSocket
┌─────────────────────────▼───────────────────────────────────┐
│                      BACKEND (FastAPI)                        │
│  Auth | MarketData | SymbolSearch | AgentEngine              │
│  PredictionEngine | ExplainabilityEngine | NewsIntelligence  │
│  InstitutionalIntelligence | OptionsIntelligence             │
│  SignalEngine | BacktestEngine | AlertEngine | Monitoring    │
└───┬──────────────┬───────────────┬────────────────┬─────────┘
    │              │               │                │
┌───▼──┐    ┌─────▼────┐   ┌──────▼──────┐  ┌──────▼──────┐
│SQLite│    │ Parquet  │   │  diskcache  │  │ JSON Files  │
│(ORM) │    │(OHLCV TS)│   │  (Cache)    │  │(Agent/Logs) │
└──────┘    └──────────┘   └─────────────┘  └─────────────┘
```

### 3.3 High-Level Data Flow

```
External APIs → DataCollectionLayer → ValidationLayer → StorageLayer
                                                              │
                                                     AgentEngine (42 agents)
                                                              │
                                                     PredictionEngine
                                                              │
                                                   ExplainabilityEngine (LLM)
                                                              │
                                                    WebSocket → Frontend
```

---

## 4. Functional Requirements

### 4.1 Core Features

#### FR-001: Global Symbol Search
- Users can search any US stock ticker, company name, ETF name, index symbol, or commodity name
- Autocomplete suggests matching symbols as user types (debounced, 300ms delay)
- On selection: trigger full data fetch, run all 42 agents, generate predictions for all 6 horizons
- Return full analysis package: OHLCV, predictions, agent outputs, options data, institutional flows, news, signals
- Keyboard shortcut: `Ctrl+K` / `Cmd+K`

#### FR-002: Market Predictions
- Generate predictions for any searched symbol across 6 horizons: 2D, 5D, 10D, 20D, 30D, 60D
- Each prediction outputs: Direction (Bullish/Bearish/Neutral), Confidence Score (0–100), Risk Score (0–100), Expected Move %, Prediction ID, Timestamp
- Predictions must be regenerable on demand

#### FR-003: 42-Agent Analysis Pipeline
- All 42 agents execute sequentially (respecting dependency order) per symbol
- Each agent produces: Agent Name, Agent Score (0–100), Signal (Bullish/Bearish/Neutral), Confidence Level, Reasoning text, Supporting Data object, Bullish Factors list, Bearish Factors list, Impact Weight, LLM-Ready Summary JSON
- Agent outputs stored permanently for auditability

#### FR-004: Explainability Engine
- Every prediction is accompanied by a full explainability breakdown:
  - Per-agent contributions with weights
  - Top bullish drivers (data-backed)
  - Top bearish drivers (data-backed)
  - Supporting evidence
  - LLM-generated 3–5 sentence analyst narrative (see Section 14)

#### FR-005: Institutional Flow Monitoring
- ETF flow tracking (inflow/outflow trends)
- SEC Form 4 insider transaction monitoring
- 13F institutional holding changes
- Dark Pool activity (FINRA ATS aggregate — degraded mode MVP)
- Whale options flow detection

#### FR-006: Options Intelligence
- Put/Call parity analysis
- Gamma Exposure (GEX) calculation and visualization
- Open Interest structure by strike and expiry
- Call Wall / Put Wall / Max Pain identification
- VIX term structure analysis
- Dealer positioning estimation

#### FR-007: Market Intelligence Dashboard
- Market Regime classification (trending/ranging/volatile/transitional)
- Market Breadth score (% stocks above MA thresholds)
- Sector Rotation heatmap
- Macro and Federal Reserve impact analysis
- Cross-asset correlation matrix
- DXY strength tracker

#### FR-008: Backtesting
- Historical walk-forward backtesting for any symbol and horizon combination
- Metrics: Win Rate, CAGR, Sharpe Ratio, Max Drawdown, Monthly P&L, Equity Curve
- Filter by date range, horizon, confidence threshold

#### FR-009: Performance Analytics
- Prediction accuracy tracking per horizon, per symbol, per agent
- Precision, Recall, F1 Score over rolling windows
- Agent performance rankings
- Confidence calibration charts

#### FR-010: Alert System
- Configurable alerts: Prediction Change, Regime Change, High Risk, Institutional Flow, Options Spike, System Health
- Delivery: Dashboard notification, email (production), future webhook
- Alert history with delivery status tracking

#### FR-011: Historical Predictions Archive
- Full searchable history of all predictions with actual outcomes
- Accuracy tracking: predicted direction vs. actual price movement at horizon expiry
- Filters: symbol, date range, confidence, outcome (correct/incorrect)

#### FR-012: AI Explanation Tab
- Dedicated tab showing all LLM-generated narratives
- Browse, search, filter by symbol, direction, horizon, date
- Full narrative text + key data points that drove reasoning
- "Regenerate Explanation" button per prediction

### 4.2 User Workflows

#### 4.2.1 Symbol Search Workflow
```
User types symbol/name in global search bar
  → Autocomplete suggestions appear (debounced 300ms)
  → User selects symbol
  → Backend: fetch OHLCV data (yfinance)
  → Backend: run all 42 agents for symbol
  → Backend: run prediction engine (6 horizons)
  → Backend: trigger LLM explanation generation (async)
  → Frontend: render Symbol Detail Panel
    ├── Symbol header (name, ticker, price, change%)
    ├── Price chart with selectable timeframes
    ├── Prediction cards (2D, 5D, 10D, 20D, 30D, 60D)
    ├── Agent Analysis section (all 42 agents)
    ├── Institutional Flows section
    ├── Options Intelligence section
    ├── News & Sentiment section
    ├── Signal Explorer
    ├── Historical Predictions
    ├── Backtesting results
    └── AI Explanation Panel (renders when ready via WebSocket)
  → Panel is dismissible; returns to main dashboard
```

#### 4.2.2 Prediction Generation Workflow
```
Trigger: Symbol search, scheduled refresh, or manual regenerate
  → DataCollectionLayer: fetch/validate/cache required data
  → AgentEngine: execute agents in dependency order (Agents 1→6 → 7→14 → 15→20 → 21→26 → 27→29 → 30→33 + 34 + 35→42)
  → PredictionEngine: aggregate agent outputs, run ensemble models
  → Output: Prediction object (direction, confidence, risk, expected_move, horizon)
  → ExplainabilityEngine: compile agent attributions + bullish/bearish drivers
  → LLM Engine: async call → generate narrative → store in PredictionExplanations
  → WebSocket broadcast: prediction ready + explanation ready (when available)
```

#### 4.2.3 Admin Workflow
```
Admin logs in (Super Admin / Admin role required)
  → Admin panel shows: System health, all 42 agent statuses, prediction quality, data source health
  → Can: manually trigger agent runs, pause/resume agents, view full logs, manage users, view ML model versions
  → Configuration: modify agent weights, prediction thresholds, refresh frequencies, API key rotation
```

---

## 5. Non-Functional Requirements

### 5.1 Performance
- API response time (cached predictions): ≤ 200ms at 95th percentile
- API response time (uncached symbol search): ≤ 5000ms (full 42-agent run)
- WebSocket message delivery latency: ≤ 500ms
- Frontend initial load time: ≤ 3 seconds on 10Mbps connection
- Frontend Time to Interactive: ≤ 4 seconds

### 5.2 Scalability
- MVP: 1–10 concurrent users, single server, SQLite + Parquet
- Production: 100–500 concurrent users, PostgreSQL + TimescaleDB + Redis
- Enterprise: 1000+ concurrent users, cloud-native, multi-region

### 5.3 Reliability
- System uptime target: ≥ 99.5% during US market hours
- Agent failure isolation: one agent failure must not halt the full pipeline (graceful degradation)
- Data source fallback: every agent has primary, secondary, and fallback data sources
- Prediction always generated even if some agents fail (with degraded confidence flag)

### 5.4 Security
- All endpoints require JWT authentication except `/health` and `/api/v1/auth/login`
- RBAC with four roles: Super Admin, Admin, Analyst, Viewer
- All API keys stored in environment variables — never hardcoded
- Rate limiting on all public endpoints
- Audit logging for all write operations and admin actions
- HTTPS enforced in all non-development environments

### 5.5 Maintainability
- All backend modules independently testable
- All agents follow identical interface contract (`BaseAgent`)
- Database schema versioned with Alembic migrations
- All configuration externalized (no magic values in code)
- Structured JSON logging for all application events

### 5.6 Data Integrity
- Market data validated on ingestion (price reasonableness checks, volume sanity, completeness checks)
- Agent outputs validated before storage (score range 0–100, signal must be one of Bullish/Bearish/Neutral)
- Prediction IDs are globally unique UUIDs
- All predictions immutable after generation (new prediction = new record, not update)

---

## 6. Technology Stack

### 6.1 Frontend

| Technology | Version | Purpose |
|-----------|---------|---------|
| Next.js | Latest Stable | React framework, CSR mode |
| JavaScript | ES2022+ | Language (no TypeScript) |
| Tailwind CSS | Latest | Utility-first styling |
| ShadCN UI | Latest | Accessible component library |
| Recharts | Latest | Financial charts and data visualization |
| Framer Motion | Latest | Animations and transitions |
| Zustand | Latest | Global state management |
| TanStack Query | Latest | Server state, caching, refetching |
| Axios | Latest | HTTP client |
| WebSocket (native) | — | Real-time data streaming |

### 6.2 Backend

| Technology | Version | Purpose |
|-----------|---------|---------|
| Python | 3.12 | Runtime |
| FastAPI | Latest | Web framework, async API |
| SQLAlchemy | 2.x | ORM (SQLite MVP, PostgreSQL production) |
| Alembic | Latest | Database schema migrations |
| APScheduler | Latest | Background job scheduling (SQLite job store) |
| Pydantic | v2 | Request/response validation |
| python-jose | Latest | JWT creation and validation |
| passlib | Latest | Password hashing (bcrypt) |
| httpx | Latest | Async HTTP client for external APIs |
| diskcache | Latest | File-based caching (Redis replacement for MVP) |
| pandas | Latest | Data manipulation |
| numpy | Latest | Numerical computations |
| pyarrow | Latest | Parquet file I/O |
| yfinance | Latest | Yahoo Finance market data |
| pandas-datareader | Latest | Stooq and other data sources |
| python-dotenv | Latest | Environment variable loading |
| python-json-logger | Latest | Structured JSON logging |
| prometheus-fastapi-instrumentator | Latest | Prometheus metrics endpoint |

### 6.3 Machine Learning

| Technology | Purpose |
|-----------|---------|
| LightGBM | Primary gradient boosting classifier |
| XGBoost | Secondary gradient boosting classifier |
| CatBoost | Categorical feature gradient boosting |
| Scikit-learn (Random Forest, Extra Trees, Logistic Regression) | Ensemble members |
| SHAP | Feature explainability (SHAP values) |
| MLflow | Model registry, experiment tracking |
| joblib | Model serialization |

### 6.4 Data Storage (MVP — Zero External Infrastructure)

| Storage | Technology | Purpose |
|---------|-----------|---------|
| Relational | SQLite via SQLAlchemy | Users, agents, predictions, signals, alerts, logs |
| Time-Series | Parquet files (pandas + pyarrow) | OHLCV data, options snapshots, VIX history |
| Cache | diskcache | API responses, agent outputs, LLM explanations (24hr TTL) |
| Config/Outputs | JSON flat files | Agent run outputs, prediction logs |

### 6.5 Deployment

| Environment | Frontend | Backend | Database | Cache |
|-------------|----------|---------|----------|-------|
| MVP | Vercel | Railway / Render | SQLite (file) | diskcache (file) |
| Production | Vercel Pro | Railway Pro / Dedicated VPS | PostgreSQL + TimescaleDB | Managed Redis |
| Enterprise | Vercel Enterprise | AWS/GCP/Azure | Aurora PostgreSQL | ElastiCache Redis |

---

## 7. Frontend Architecture

### 7.1 Architecture Style

**Client-Side Rendered (CSR) Next.js Application.** The app shell is rendered on the client. API calls go directly to the FastAPI backend. SSR is not used for data pages (data is user-specific and real-time).

### 7.2 Page Hierarchy

```
/ (Root)
├── /login                          — Authentication page
├── /dashboard                      — Main dashboard (default after login)
├── /predictions                    — All active predictions
├── /market-intelligence            — Regime, breadth, macro analysis
├── /news                           — News feed, earnings, economic calendar
├── /agents                         — All 42 agent panels
├── /signals                        — Signal explorer
├── /institutional-flows            — ETF flows, 13F, dark pool, insider
├── /options-intelligence           — GEX, OI, put/call, dealer positioning
├── /backtesting                    — Strategy backtesting
├── /performance                    — Prediction performance analytics
├── /history                        — Historical predictions archive
├── /alerts                         — Alert management
├── /explanations                   — AI Explanation narratives tab
├── /settings                       — User preferences
└── /admin                          — Admin operations center
    ├── /admin/system               — System health
    ├── /admin/agents               — Agent monitoring (42 agents)
    ├── /admin/predictions          — Prediction monitoring
    ├── /admin/data-sources         — Data source health
    ├── /admin/api-health           — API monitoring
    ├── /admin/data-quality         — Data quality dashboard
    ├── /admin/alerts               — Alert monitoring
    ├── /admin/logs                 — Log viewer
    ├── /admin/users                — User management
    ├── /admin/models               — ML model monitoring
    └── /admin/config               — System configuration
```

### 7.3 Component Hierarchy

```
components/
├── layout/
│   ├── MainLayout.jsx              — Top nav, sidebar, content area
│   ├── Sidebar.jsx                 — Navigation menu
│   ├── TopNav.jsx                  — Logo, search bar, user menu, theme toggle
│   └── AdminLayout.jsx             — Admin-specific layout wrapper
│
├── search/
│   ├── GlobalSearchBar.jsx         — Full-width search with Ctrl+K shortcut
│   ├── SearchAutocomplete.jsx      — Dropdown suggestions
│   └── SymbolDetailPanel.jsx       — Overlay panel showing full symbol analysis
│
├── dashboard/
│   ├── MarketRegimeWidget.jsx
│   ├── MarketDirectionWidget.jsx
│   ├── ConfidenceScoreWidget.jsx
│   ├── RiskScoreWidget.jsx
│   ├── ExpectedMoveWidget.jsx
│   ├── MarketBreadthWidget.jsx
│   ├── MomentumScoreWidget.jsx
│   ├── VIXStructureWidget.jsx
│   ├── DXYStrengthWidget.jsx
│   ├── SectorRotationWidget.jsx
│   ├── InstitutionalFlowSummary.jsx
│   ├── ETFFlowSummary.jsx
│   ├── WhaleFlowSummary.jsx
│   ├── BullishDriversWidget.jsx
│   ├── BearishDriversWidget.jsx
│   ├── AgentConsensusWidget.jsx
│   ├── PredictionTimeline.jsx
│   ├── HistoricalAccuracyWidget.jsx
│   ├── ActiveAlertsWidget.jsx
│   └── MajorRisksWidget.jsx
│
├── predictions/
│   ├── PredictionCard.jsx          — Single prediction display
│   ├── PredictionTable.jsx         — Sortable/filterable predictions list
│   ├── HorizonSelector.jsx         — 2D/5D/10D/20D/30D/60D tabs
│   └── PredictionFilters.jsx
│
├── agents/
│   ├── AgentCard.jsx               — Single agent panel
│   ├── AgentGrid.jsx               — Grid of all 42 agents
│   ├── AgentCategoryGroup.jsx      — Grouped by category
│   └── AgentDetailModal.jsx        — Full agent breakdown
│
├── charts/
│   ├── PriceChart.jsx              — OHLCV candlestick/line chart
│   ├── AccuracyTrendChart.jsx
│   ├── GEXChart.jsx
│   ├── OIHeatmap.jsx
│   ├── CorrelationHeatmap.jsx
│   ├── SectorRotationChart.jsx
│   ├── BreadthHistoryChart.jsx
│   ├── EquityCurveChart.jsx
│   └── RegimeTimelineChart.jsx
│
├── explanations/
│   ├── ExplanationCard.jsx         — LLM narrative display card
│   ├── ExplanationList.jsx         — Browsable list of explanations
│   └── ExplanationFilters.jsx
│
├── institutional/
│   ├── ETFFlowPanel.jsx
│   ├── DarkPoolPanel.jsx
│   ├── InsiderTransactionPanel.jsx
│   ├── ThirteenFPanel.jsx
│   └── WhaleFlowPanel.jsx
│
├── options/
│   ├── GammaExposurePanel.jsx
│   ├── OIStructurePanel.jsx
│   ├── PutCallPanel.jsx
│   ├── VolatilityPanel.jsx
│   └── DealerPositioningPanel.jsx
│
├── alerts/
│   ├── AlertCard.jsx
│   ├── AlertList.jsx
│   └── AlertCreator.jsx
│
├── ui/                             — ShadCN base components (Button, Card, Badge, etc.)
└── admin/                          — Admin-specific components (see Section 8)
```

### 7.4 Global Search Bar Design

**Position:** Top of dashboard, full-width, always visible above all widgets  
**Placeholder:** `"Search any US stock, index, ETF, or commodity... (e.g. AAPL, TSLA, Gold, Crude Oil, SPY)"`  
**Behavior:**
- Input debounced at 300ms before triggering autocomplete API call
- Autocomplete API: `GET /api/v1/symbols/search?q={query}&limit=10`
- Results grouped by type: Stocks, ETFs, Indices, Commodities
- On Enter or result click: opens `SymbolDetailPanel` as full-page overlay
- Panel is dismissible via `Esc` or close button, returns to main dashboard
- Keyboard shortcut: `Ctrl+K` (Windows/Linux) / `Cmd+K` (macOS) — opens search from anywhere in the app

**SymbolDetailPanel Sections (in order):**
1. Symbol Header (ticker, full name, current price, change%, market cap if available)
2. Price Chart (Recharts, selectable timeframes: 1D / 1W / 1M / 3M / 6M / 1Y)
3. Prediction Cards (6 horizons, side-scrollable on mobile)
4. Agent Analysis (all 42 agents, categorized)
5. Institutional Flows (ETF flow, insider, 13F summary)
6. Options Intelligence (GEX, OI, put/call summary)
7. News & Sentiment (latest 10 articles with sentiment scores)
8. Signal Explorer (active signals for this symbol)
9. Historical Predictions (last 20 predictions for this symbol)
10. Backtesting Results (last run results)
11. AI Explanation Panel (LLM narrative — renders via WebSocket when ready, shows loading state until available)

### 7.5 State Management

**Zustand Stores:**

```javascript
// stores/marketStore.js — market-wide data
// stores/symbolStore.js — currently searched symbol and its analysis
// stores/predictionStore.js — active predictions by symbol
// stores/agentStore.js — agent statuses and outputs
// stores/alertStore.js — active alerts
// stores/uiStore.js — theme, sidebar state, search panel open/close
// stores/adminStore.js — admin metrics (only loaded for admin roles)
```

**TanStack Query Usage:**
- All API data fetching via `useQuery` hooks (automatic caching, background refetch, stale-while-revalidate)
- Mutations via `useMutation` (e.g., regenerate explanation, trigger backtest)
- Global QueryClient with default staleTime: 60 seconds for predictions, 5 minutes for agent data

**WebSocket State:**
- Single persistent WebSocket connection per session
- Channels: `market_data`, `agent_updates`, `prediction_updates`, `alerts`, `system_health`, `explanation_ready`
- On reconnect: auto-resubscribe to all channels
- WebSocket events trigger Zustand store updates (not TanStack Query cache updates — separate state)

### 7.6 Theme System

- Dark mode and Light mode
- Theme stored in `localStorage` under key `usa-swing-theme`
- Toggle available in top navigation bar
- CSS variables used throughout (Tailwind `dark:` variants + CSS custom properties)
- Default theme: Dark mode (institutional preference)

**Color Palette (Dark Mode):**
- Background: `#0a0a0f`
- Card: `#111118`
- Border: `#1e1e2e`
- Text Primary: `#e2e8f0`
- Text Secondary: `#94a3b8`
- Bullish Green: `#22c55e`
- Bearish Red: `#ef4444`
- Neutral Yellow: `#eab308`
- Accent Blue: `#3b82f6`

### 7.7 Responsive Design

| Breakpoint | Layout |
|-----------|--------|
| Mobile (< 768px) | Single column, collapsible sidebar, stacked widgets |
| Tablet (768px–1024px) | Two-column grid, icon sidebar |
| Laptop (1024px–1280px) | Three-column grid, compact sidebar |
| Desktop (> 1280px) | Full multi-column Bloomberg-style layout |

### 7.8 Frontend Folder Structure

```
frontend/
├── src/
│   ├── app/                        — Next.js App Router pages
│   │   ├── layout.jsx
│   │   ├── page.jsx                — Redirects to /dashboard
│   │   ├── login/
│   │   ├── dashboard/
│   │   ├── predictions/
│   │   ├── market-intelligence/
│   │   ├── news/
│   │   ├── agents/
│   │   ├── signals/
│   │   ├── institutional-flows/
│   │   ├── options-intelligence/
│   │   ├── backtesting/
│   │   ├── performance/
│   │   ├── history/
│   │   ├── alerts/
│   │   ├── explanations/
│   │   ├── settings/
│   │   └── admin/
│   ├── components/                 — All UI components (see 7.3)
│   ├── stores/                     — Zustand stores
│   ├── hooks/                      — Custom React hooks
│   ├── lib/
│   │   ├── api.js                  — Axios instance with auth interceptors
│   │   ├── websocket.js            — WebSocket manager
│   │   └── utils.js                — Formatters, helpers
│   ├── styles/
│   │   └── globals.css             — Tailwind imports + CSS variables
│   └── constants/
│       ├── agents.js               — Agent ID/name mapping
│       └── markets.js              — Symbol/market constants
├── public/
├── tailwind.config.js
├── next.config.js
└── package.json
```

---

## 8. Admin Panel Architecture

### 8.1 Access Control

Admin panel at `/admin/*` is accessible only to users with roles `Super Admin` or `Admin`. Route-level guard in Next.js middleware checks JWT role claim.

### 8.2 Admin Sections

#### 8.2.1 System Overview (`/admin/system`)
Displays:
- System Status badge (Healthy / Degraded / Down)
- Uptime counter
- CPU Usage (%), RAM Usage (%), Disk Usage (%), Network I/O
- Active Users count, Active Sessions count
- Today's stats: Total Predictions, Total Signals, Total Alerts generated
- Real-time charts: CPU/RAM over last 1 hour (WebSocket-updated)

#### 8.2.2 Agent Monitoring (`/admin/agents`)
Master table of all 42 agents (sequential IDs 1–42):

| Column | Description |
|--------|-------------|
| Agent # | Sequential ID (1–42) |
| Name | Agent name |
| Category | Direction / News&Macro / Institutional / Strength / Exit&Reversal / PredictionLayer / Additional / Commodity |
| Status | Healthy (green) / Warning (yellow) / Failed (red) |
| Last Run | Timestamp |
| Duration | Execution time in seconds |
| Data Freshness | Age of most recent data used |
| Confidence | Current confidence score output |
| Accuracy (30d) | 30-day rolling accuracy |
| Errors | Error count in last 24h |
| Action | Manual trigger button |

Summary cards at top: Total (42), Healthy, Warning, Failed.

#### 8.2.3 Prediction Monitoring (`/admin/predictions`)
- Total predictions generated today / this week / this month
- Accuracy %, Win Rate, False Positives, False Negatives
- Average Confidence Score
- Prediction Drift indicator (staleness of model outputs vs. actuals)
- Charts: Daily Accuracy, Weekly Accuracy, Monthly Accuracy, Accuracy by Horizon

#### 8.2.4 Data Source Monitoring (`/admin/data-sources`)
Per-source status table:

| Source | Status | Last Update | Response Time | Error Count | Rate Limit |
|--------|--------|-------------|---------------|-------------|------------|
| Yahoo Finance | — | — | — | — | N/A |
| Alpha Vantage | — | — | — | — | 25/day |
| FRED | — | — | — | — | Unlimited |
| SEC EDGAR | — | — | — | — | N/A |
| FINRA | — | — | — | — | N/A |
| CBOE | — | — | — | — | N/A |
| NewsAPI | — | — | — | — | 100/day |
| EIA | — | — | — | — | Unlimited |
| Nasdaq Data Link | — | — | — | — | Free tier |

#### 8.2.5 API Monitoring (`/admin/api-health`)
Per-endpoint metrics: endpoint path, requests/hour, success rate, error rate, avg response time, P99 response time.

#### 8.2.6 Data Quality (`/admin/data-quality`)
- Missing Data % by source and symbol
- Delayed Data % (data older than expected refresh window)
- Invalid Records count (failed validation)
- Data Freshness Score (composite)
- Data Completeness Score

#### 8.2.7 Alert Monitoring (`/admin/alerts`)
Active alerts, alert history, failed delivery count, delivery status per channel (dashboard, email).

#### 8.2.8 Logs (`/admin/logs`)
Searchable, filterable log viewer. Log types: Application, API, Agent, Prediction, Error, Audit. Fields displayed: Timestamp, Severity, Source, Message. Supports text search and severity filter.

#### 8.2.9 User Management (`/admin/users`)
CRUD interface for user accounts. Columns: Username, Email, Role, Last Login, Active Sessions, Created At. Role assignment: Super Admin / Admin / Analyst / Viewer.

#### 8.2.10 Model Monitoring (`/admin/models`)
Per-model table: Model Name, Version, Training Date, Validation Score, Production Accuracy (30d), Drift Score. Models: LightGBM, XGBoost, Random Forest, Logistic Regression, CatBoost, Extra Trees.

#### 8.2.11 System Configuration (`/admin/config`)
Admin-editable settings:
- Agent weights (per agent, 0.0–1.0 slider)
- Prediction confidence thresholds
- Alert trigger thresholds
- Data refresh frequencies per source
- API key rotation (masked display, update form)

### 8.3 Admin RBAC

| Permission | Super Admin | Admin | Analyst | Viewer |
|-----------|-------------|-------|---------|--------|
| View all admin sections | ✓ | ✓ | ✗ | ✗ |
| Edit system configuration | ✓ | ✗ | ✗ | ✗ |
| Manage users | ✓ | ✓ | ✗ | ✗ |
| Trigger agent runs | ✓ | ✓ | ✗ | ✗ |
| View logs | ✓ | ✓ | ✗ | ✗ |
| View predictions | ✓ | ✓ | ✓ | ✓ |
| Regenerate explanations | ✓ | ✓ | ✓ | ✗ |

---

## 9. Backend Architecture

### 9.1 Architecture Style

**Modular Monolith** with Domain-Driven Design and Service-Oriented internals. All modules reside in a single deployable process. Module boundaries are strictly enforced by directory structure and import rules. Migration to microservices is possible by extracting each module directory into a separate service.

### 9.2 Backend Folder Structure

```
backend/
├── main.py                         — FastAPI app factory, router registration
├── config.py                       — Settings (loaded from .env via pydantic-settings)
├── dependencies.py                 — Shared FastAPI dependencies (auth, db session)
│
├── modules/
│   ├── auth/
│   │   ├── router.py               — POST /auth/login, /auth/logout, /auth/refresh
│   │   ├── service.py              — AuthService: login, token creation, validation
│   │   ├── models.py               — SQLAlchemy: User, UserSession
│   │   └── schemas.py              — Pydantic: LoginRequest, TokenResponse
│   │
│   ├── market_data/
│   │   ├── router.py               — GET /market/ohlcv, /market/indicators
│   │   ├── service.py              — MarketDataService: fetch, validate, store
│   │   ├── collectors/
│   │   │   ├── yahoo_collector.py  — yfinance wrapper
│   │   │   ├── alpha_vantage.py    — Alpha Vantage API client
│   │   │   ├── stooq_collector.py  — pandas_datareader Stooq wrapper
│   │   │   ├── fred_collector.py   — FRED API client
│   │   │   └── eia_collector.py    — EIA API client (crude oil, natural gas)
│   │   ├── validators.py           — Data validation rules
│   │   ├── models.py               — SQLAlchemy: Symbols, Markets
│   │   └── schemas.py
│   │
│   ├── symbol_search/
│   │   ├── router.py               — GET /symbols/search, /symbols/{symbol}
│   │   ├── service.py              — SymbolSearchService: search, full analysis fetch
│   │   ├── symbol_registry.py      — In-memory symbol list (loaded at startup from JSON)
│   │   └── schemas.py
│   │
│   ├── agents/
│   │   ├── router.py               — GET /agents, /agents/{id}/output
│   │   ├── engine.py               — AgentEngine: orchestrates execution of all 42 agents
│   │   ├── registry.py             — AgentRegistry: maps agent IDs to agent classes
│   │   ├── scheduler.py            — APScheduler job definitions for all 42 agents
│   │   ├── base_agent.py           — BaseAgent abstract class (all agents inherit this)
│   │   ├── direction/
│   │   │   ├── agent_01_regime_detection.py
│   │   │   ├── agent_02_trend_structure.py
│   │   │   ├── agent_03_market_breadth.py
│   │   │   ├── agent_04_market_momentum.py
│   │   │   ├── agent_05_trend_following.py
│   │   │   └── agent_06_hmm_market_state.py
│   │   ├── news_macro/
│   │   │   ├── agent_07_news_analyst.py
│   │   │   ├── agent_08_earnings_sentiment.py
│   │   │   ├── agent_09_event_detection.py
│   │   │   ├── agent_10_macro_news_impact.py
│   │   │   ├── agent_11_macro_analyst.py
│   │   │   ├── agent_12_federal_reserve.py
│   │   │   ├── agent_13_global_liquidity.py
│   │   │   └── agent_14_dollar_strength.py
│   │   ├── institutional/
│   │   │   ├── agent_15_sector_rotation.py
│   │   │   ├── agent_16_dark_pool_flow.py
│   │   │   ├── agent_17_13f_accumulation.py
│   │   │   ├── agent_18_whale_options_flow.py
│   │   │   ├── agent_19_insider_transactions.py
│   │   │   └── agent_20_etf_flow_intelligence.py
│   │   ├── strength/
│   │   │   ├── agent_21_put_call_parity.py
│   │   │   ├── agent_22_gamma_exposure.py
│   │   │   ├── agent_23_factor_crowding.py
│   │   │   ├── agent_24_uncertainty.py
│   │   │   ├── agent_25_relative_strength.py
│   │   │   └── agent_26_vix_structure.py
│   │   ├── exit_reversal/
│   │   │   ├── agent_27_correlation_decay.py
│   │   │   ├── agent_28_cross_asset_correlation.py
│   │   │   └── agent_29_market_leadership.py
│   │   ├── prediction_layer/
│   │   │   ├── agent_30_signal_aggregation.py
│   │   │   ├── agent_31_ensemble_model.py
│   │   │   ├── agent_32_confidence_scoring.py
│   │   │   └── agent_33_final_prediction_engine.py
│   │   ├── additional/
│   │   │   └── agent_34_oi_structure.py
│   │   └── commodity/
│   │       ├── agent_35_crude_oil.py
│   │       ├── agent_36_gold_precious_metals.py
│   │       ├── agent_37_natural_gas.py
│   │       ├── agent_38_silver.py
│   │       ├── agent_39_copper.py
│   │       ├── agent_40_commodity_momentum.py
│   │       ├── agent_41_commodity_sentiment.py
│   │       └── agent_42_commodity_flow_positioning.py
│   │
│   ├── predictions/
│   │   ├── router.py               — GET/POST /predictions, /predictions/{id}
│   │   ├── engine.py               — PredictionEngine: ensemble aggregation
│   │   ├── models.py               — SQLAlchemy: Predictions, PredictionReasons, PredictionContributors
│   │   └── schemas.py
│   │
│   ├── explainability/
│   │   ├── router.py               — GET /explanations/{id}, POST /explanations/regenerate/{id}
│   │   ├── engine.py               — ExplainabilityEngine: attribution + LLM narrative
│   │   ├── llm_client.py           — Grok API client wrapper
│   │   ├── prompt_builder.py       — ExplanationPromptBuilder: structured prompt assembly
│   │   ├── fallback_builder.py     — Template-based fallback narrative generator
│   │   ├── models.py               — SQLAlchemy: PredictionExplanations
│   │   └── schemas.py
│   │
│   ├── news/
│   │   ├── router.py
│   │   ├── service.py              — NewsIntelligenceEngine
│   │   ├── sentiment.py            — TextBlob/VADER sentiment scoring
│   │   ├── models.py               — NewsArticles, NewsSentiment
│   │   └── schemas.py
│   │
│   ├── institutional/
│   │   ├── router.py
│   │   ├── service.py              — InstitutionalIntelligenceEngine
│   │   ├── models.py               — InstitutionalFlows, DarkPoolActivity, InsiderTransactions, ThirteenFHoldings
│   │   └── schemas.py
│   │
│   ├── options/
│   │   ├── router.py
│   │   ├── service.py              — OptionsIntelligenceEngine
│   │   ├── gex_calculator.py       — Gamma Exposure calculation
│   │   ├── models.py               — OptionsData, VIXData
│   │   └── schemas.py
│   │
│   ├── signals/
│   │   ├── router.py
│   │   ├── service.py              — SignalEngine
│   │   ├── models.py               — Signals
│   │   └── schemas.py
│   │
│   ├── backtesting/
│   │   ├── router.py
│   │   ├── engine.py               — BacktestEngine: walk-forward testing
│   │   ├── models.py               — Backtests, BacktestResults
│   │   └── schemas.py
│   │
│   ├── alerts/
│   │   ├── router.py
│   │   ├── service.py              — AlertEngine
│   │   ├── delivery.py             — Email delivery (production)
│   │   ├── models.py               — Alerts
│   │   └── schemas.py
│   │
│   ├── monitoring/
│   │   ├── router.py               — GET /admin/system-metrics, /admin/api-health
│   │   ├── service.py              — MonitoringEngine
│   │   ├── models.py               — SystemMetrics, APIHealth, DataSourceHealth, AgentHealth
│   │   └── schemas.py
│   │
│   └── admin/
│       ├── router.py               — All /admin/* endpoints
│       └── service.py              — AdminService: user management, config management
│
├── core/
│   ├── database.py                 — SQLAlchemy engine + session factory (SQLite MVP)
│   ├── cache.py                    — CacheService abstraction (diskcache backend MVP)
│   ├── security.py                 — JWT utils, password hashing
│   ├── exceptions.py               — Custom exception classes
│   ├── middleware.py               — Request logging, rate limiting
│   └── websocket_manager.py        — WebSocket connection pool + broadcast
│
├── data/                           — Runtime data files (gitignored except templates)
│   ├── usa_swing.db                — SQLite database file
│   ├── scheduler.db                — APScheduler SQLite job store
│   ├── cache/                      — diskcache directory
│   ├── market_data/                — Parquet files directory
│   │   └── ohlcv/{symbol}/{timeframe}.parquet
│   └── symbols/
│       └── symbol_registry.json    — Master symbol list (all US stocks, ETFs, indices, commodities)
│
├── logs/                           — JSON log files
│   ├── app.log
│   ├── agents.log
│   ├── predictions.log
│   └── errors.log
│
├── ml/
│   ├── features/
│   │   ├── feature_builder.py      — Builds feature matrix from agent outputs
│   │   └── feature_store.py        — Parquet-backed feature store
│   ├── models/
│   │   ├── ensemble.py             — Ensemble model wrapper
│   │   └── registry.py             — MLflow model registry client
│   ├── training/
│   │   ├── trainer.py              — Model training pipeline
│   │   └── validator.py            — Walk-forward validation
│   └── artifacts/                  — Saved model files (MLflow tracking)
│
├── tests/
│   ├── unit/                       — Unit tests per module
│   ├── integration/                — Integration tests (API + DB)
│   └── fixtures/                   — Test data fixtures
│
├── alembic/                        — Alembic migrations
│   ├── env.py
│   └── versions/
│
├── .env                            — Environment variables (never committed)
├── .env.example                    — Template for .env
├── requirements.txt
└── alembic.ini
```

### 9.3 BaseAgent Interface Contract

All 42 agents must implement the following interface. No agent may deviate from this contract.

```python
# backend/modules/agents/base_agent.py
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional
from enum import Enum

class Signal(str, Enum):
    BULLISH = "Bullish"
    BEARISH = "Bearish"
    NEUTRAL = "Neutral"

@dataclass
class AgentOutput:
    agent_id: int                    # Sequential 1–42
    agent_name: str
    signal: Signal
    score: float                     # 0.0–100.0
    confidence: float                # 0.0–100.0
    weight: float                    # 0.0–1.0 (normalized impact weight)
    reasoning: str                   # Human-readable explanation
    bullish_factors: list[str]       # List of bullish data points
    bearish_factors: list[str]       # List of bearish data points
    supporting_data: dict            # Raw data values used (for audit)
    llm_ready_summary: dict          # {"agent": str, "signal": str, "finding": str} (max 200 chars for finding)
    data_freshness: str              # ISO 8601 timestamp of most recent data used
    execution_time_ms: int
    error: Optional[str] = None      # None if successful, error message if degraded

class BaseAgent(ABC):
    agent_id: int
    agent_name: str
    category: str
    refresh_frequency: str           # "realtime" | "5min" | "hourly" | "daily" | "weekly"
    dependencies: list[int]          # IDs of agents that must run before this one
    tier: int                        # 1 (MVP) | 2 (Production) | 3 (Future)

    @abstractmethod
    def run(self, symbol: str, context: dict) -> AgentOutput:
        """Execute agent analysis for the given symbol. context contains outputs of dependency agents."""
        pass

    def validate_output(self, output: AgentOutput) -> bool:
        assert 0.0 <= output.score <= 100.0
        assert 0.0 <= output.confidence <= 100.0
        assert output.signal in Signal.__members__.values()
        return True
```

### 9.4 Agent Execution Engine

```
AgentEngine.run(symbol, horizons):
  1. Load context dict (empty initially)
  2. Execute Direction Agents (1–6) in parallel (no inter-dependencies within group)
  3. Execute News & Macro Agents (7–14) in parallel
  4. Execute Institutional Agents (15–20) in parallel
  5. Execute Strength Agents (21–26) in parallel
  6. Execute Exit & Reversal Agents (27–29) in parallel
  7. Execute Additional Agent 34 in parallel with above
  8. Execute Commodity Agents (35–42) in parallel
  9. Execute Prediction Layer sequentially: 30 → 31 → 32 → 33
     (Agent 30 depends on all previous; Agent 33 depends on 30, 31, 32)
  10. On Agent 33 completion: trigger ExplainabilityEngine (async background task)
  11. Store all AgentOutputs to SQLite + JSON files
  12. Return prediction
```

### 9.5 Background Job Schedule (APScheduler)

| Job | Frequency | Description |
|-----|-----------|-------------|
| collect_market_data | Every 15 min (market hours) | Fetch OHLCV for all watched symbols |
| run_direction_agents | Every 15 min (market hours) | Agents 1–6 |
| run_news_macro_agents | Every 15 min | Agents 7–14 |
| run_institutional_agents | Daily at 6:30 AM ET | Agents 15–20 |
| run_strength_agents | Every 30 min | Agents 21–26 |
| run_commodity_agents | Every 30 min | Agents 35–42 |
| run_prediction_pipeline | Every 30 min (market hours), once daily (after-hours) | Full 42-agent run + prediction |
| collect_economic_data | Daily at 7:00 AM ET | FRED data refresh |
| collect_news | Every 30 min | NewsAPI + Yahoo Finance news |
| run_backtests | Weekly Sunday 2:00 AM | Full backtest refresh |
| retrain_models | Weekly Saturday midnight | ML model retraining |
| cleanup_old_data | Daily at 3:00 AM | Log rotation, old cache cleanup |

### 9.6 Error Handling Strategy

- **Global Exception Handler:** FastAPI middleware catches all unhandled exceptions, logs them, returns structured JSON error response
- **Agent Failure Isolation:** If any agent raises an exception, `AgentEngine` catches it, logs it, marks agent output as `error=<message>`, continues with remaining agents
- **Data Source Fallback:** Each collector implements `primary → secondary → fallback` source chain with automatic failover
- **Circuit Breaker Pattern:** After 3 consecutive failures, a data source collector is marked as `circuit_open` for 10 minutes before retry
- **Retry Logic:** All external HTTP requests use exponential backoff: 3 retries, delays of 1s, 2s, 4s
- **Graceful Degradation:** Predictions still generated if ≤ 10 agents fail; confidence score auto-penalized by number of failed agents

---

## 10. Database Architecture

### 10.1 Storage Strategy

| Data Type | Storage | Format | Rationale |
|-----------|---------|--------|-----------|
| Users, sessions, roles | SQLite | Rows | Relational, low volume |
| Agent definitions, runs, outputs | SQLite | Rows | Structured, auditable |
| Predictions, signals, alerts | SQLite | Rows | Structured, queryable |
| News articles, sentiment | SQLite | Rows | Structured |
| Institutional flows, options snapshots | SQLite | Rows | Structured |
| OHLCV time-series (all symbols) | Parquet files | Columnar | High volume, read-optimized |
| Options chain snapshots | Parquet files | Columnar | Large, append-only |
| API response cache, agent output cache | diskcache | Key-value | Fast TTL-based caching |
| LLM explanation cache | diskcache | Key-value | 24hr TTL |
| Application/agent/prediction logs | JSON files | Append-only | Human-readable audit trail |

### 10.2 SQLAlchemy Model Definitions

```python
# All models use SQLAlchemy 2.x declarative style
# All tables include: id (UUID primary key), created_at, updated_at

### Users
class User(Base):
    __tablename__ = "users"
    id: UUID (PK)
    username: str (unique)
    email: str (unique)
    hashed_password: str
    role: Enum("super_admin", "admin", "analyst", "viewer")
    is_active: bool (default True)
    last_login: datetime | null
    settings: JSON (dashboard layout, preferences, default symbols)
    created_at: datetime
    updated_at: datetime

### UserSessions
class UserSession(Base):
    __tablename__ = "user_sessions"
    id: UUID (PK)
    user_id: UUID (FK → users.id)
    access_token: str
    refresh_token: str
    device_info: str
    ip_address: str
    expires_at: datetime
    created_at: datetime
    revoked_at: datetime | null

### Symbols
class Symbol(Base):
    __tablename__ = "symbols"
    id: UUID (PK)
    ticker: str (unique, indexed)
    name: str
    asset_type: Enum("stock", "etf", "index", "commodity", "futures")
    exchange: str  # NYSE, NASDAQ, AMEX, CBOE, CME, etc.
    sector: str | null
    industry: str | null
    yfinance_ticker: str   # May differ (e.g. GC=F for gold futures)
    is_active: bool
    metadata: JSON
    created_at: datetime

### AgentDefinitions
class AgentDefinition(Base):
    __tablename__ = "agent_definitions"
    id: int (PK — sequential 1–42)
    name: str
    category: Enum("direction","news_macro","institutional","strength","exit_reversal","prediction_layer","additional","commodity")
    description: str
    tier: int (1|2|3)
    refresh_frequency: str
    dependencies: JSON (list of agent IDs)
    default_weight: float
    is_active: bool

### AgentRuns
class AgentRun(Base):
    __tablename__ = "agent_runs"
    id: UUID (PK)
    agent_id: int (FK → agent_definitions.id)
    symbol: str
    started_at: datetime
    completed_at: datetime | null
    duration_ms: int | null
    status: Enum("running", "success", "failed", "degraded")
    error_message: str | null

### AgentOutputs
class AgentOutput(Base):
    __tablename__ = "agent_outputs"
    id: UUID (PK)
    run_id: UUID (FK → agent_runs.id)
    agent_id: int
    symbol: str
    signal: Enum("Bullish", "Bearish", "Neutral")
    score: float
    confidence: float
    weight: float
    reasoning: str
    bullish_factors: JSON (list[str])
    bearish_factors: JSON (list[str])
    supporting_data: JSON
    llm_ready_summary: JSON
    data_freshness: datetime
    created_at: datetime

### Predictions
class Prediction(Base):
    __tablename__ = "predictions"
    id: UUID (PK)
    symbol: str (indexed)
    direction: Enum("Bullish", "Bearish", "Neutral")
    confidence: float
    risk_score: float
    expected_move_pct: float
    horizon_days: int  # 2|5|10|20|30|60
    prediction_date: date
    expiry_date: date
    status: Enum("active", "expired", "resolved")
    actual_direction: Enum("Bullish", "Bearish", "Neutral") | null
    actual_move_pct: float | null
    is_correct: bool | null
    degraded_agents: JSON (list of failed agent IDs)
    created_at: datetime

### PredictionReasons
class PredictionReason(Base):
    __tablename__ = "prediction_reasons"
    id: UUID (PK)
    prediction_id: UUID (FK → predictions.id)
    factor_type: Enum("bullish", "bearish")
    factor: str
    supporting_data: str
    agent_id: int | null

### PredictionContributors
class PredictionContributor(Base):
    __tablename__ = "prediction_contributors"
    id: UUID (PK)
    prediction_id: UUID (FK → predictions.id)
    agent_id: int
    agent_name: str
    signal: str
    score: float
    weight: float
    impact: float  # Normalized contribution to final score

### PredictionExplanations
class PredictionExplanation(Base):
    __tablename__ = "prediction_explanations"
    id: UUID (PK)
    prediction_id: UUID (FK → predictions.id, unique)
    symbol: str
    horizon_days: int
    narrative_text: str  # LLM-generated analyst narrative (up to 2000 chars)
    model_used: str      # LLM model identifier used for generation
    prompt_snapshot: JSON # Full structured prompt sent to LLM (for auditability)
    top_bullish_factors: JSON  # list of top 3 bullish data points included in prompt
    top_bearish_factors: JSON  # list of top 3 bearish data points included in prompt
    generation_status: Enum("pending", "complete", "failed")
    fallback_used: bool   # True if template fallback was used instead of LLM
    generated_at: datetime | null
    created_at: datetime

### Signals
class Signal(Base):
    __tablename__ = "signals"
    id: UUID (PK)
    symbol: str (indexed)
    signal_type: Enum("bullish", "bearish", "neutral")
    signal_name: str
    strength: float
    confidence: float
    source_agent_id: int
    supporting_evidence: str
    created_at: datetime
    expires_at: datetime | null

### NewsArticles
class NewsArticle(Base):
    __tablename__ = "news_articles"
    id: UUID (PK)
    headline: str
    source: str
    url: str (unique)
    published_at: datetime
    symbols: JSON (list of related tickers)
    impact_score: float
    sentiment_score: float
    created_at: datetime

### NewsSentiment
class NewsSentiment(Base):
    __tablename__ = "news_sentiment"
    id: UUID (PK)
    article_id: UUID (FK → news_articles.id)
    symbol: str
    bullish_score: float
    bearish_score: float
    neutral_score: float
    composite_score: float
    analyzed_at: datetime

### InstitutionalFlows
class InstitutionalFlow(Base):
    __tablename__ = "institutional_flows"
    id: UUID (PK)
    symbol: str
    flow_type: Enum("etf_inflow", "etf_outflow", "fund_flow")
    amount: float
    source: str
    flow_date: date
    created_at: datetime

### DarkPoolActivity
class DarkPoolActivity(Base):
    __tablename__ = "dark_pool_activity"
    id: UUID (PK)
    symbol: str
    volume: float | null       # May be unavailable in MVP (aggregate only)
    accumulation_score: float
    distribution_score: float
    source: str                # "FINRA_ATS" (aggregate MVP) or "Unusual_Whales" (production)
    is_degraded: bool          # True when only FINRA aggregate data available
    data_date: date
    created_at: datetime

### InsiderTransactions
class InsiderTransaction(Base):
    __tablename__ = "insider_transactions"
    id: UUID (PK)
    symbol: str
    insider_name: str
    transaction_type: Enum("purchase", "sale")
    shares: int
    price_per_share: float
    total_value: float
    transaction_date: date
    filing_date: date
    sec_url: str

### ThirteenFHoldings
class ThirteenFHolding(Base):
    __tablename__ = "thirteen_f_holdings"
    id: UUID (PK)
    institution_name: str
    symbol: str
    shares: int
    value: float
    quarter: str  # e.g. "2024Q4"
    change_pct: float | null   # Change vs previous quarter
    filing_date: date

### OptionsData (snapshot stored in Parquet; metadata in SQLite)
class OptionsSnapshot(Base):
    __tablename__ = "options_snapshots"
    id: UUID (PK)
    symbol: str
    snapshot_date: date
    put_call_ratio: float
    max_pain: float
    call_wall: float
    put_wall: float
    gamma_exposure: float
    total_open_interest: int
    parquet_path: str         # Path to full chain Parquet file
    created_at: datetime

### VIXData
class VIXData(Base):
    __tablename__ = "vix_data"
    id: UUID (PK)
    date: date (unique)
    vix: float
    vix9d: float | null
    vix3m: float | null
    vix6m: float | null
    term_structure: Enum("contango", "backwardation", "flat")
    created_at: datetime

### CommodityData
class CommodityData(Base):
    __tablename__ = "commodity_data"
    id: UUID (PK)
    symbol: str
    data_date: date
    open_interest: int | null
    inventory_level: float | null
    supply_change_pct: float | null
    source: str
    metadata: JSON
    created_at: datetime

### Backtests / BacktestResults
class Backtest(Base):
    __tablename__ = "backtests"
    id: UUID (PK)
    symbol: str
    horizon_days: int
    start_date: date
    end_date: date
    strategy: str
    status: Enum("pending", "running", "complete", "failed")
    created_at: datetime

class BacktestResult(Base):
    __tablename__ = "backtest_results"
    id: UUID (PK)
    backtest_id: UUID (FK → backtests.id)
    win_rate: float
    cagr: float
    sharpe_ratio: float
    max_drawdown: float
    total_trades: int
    profitable_trades: int
    monthly_returns: JSON
    equity_curve: JSON
    created_at: datetime

### Alerts
class Alert(Base):
    __tablename__ = "alerts"
    id: UUID (PK)
    alert_type: Enum("prediction","regime_change","high_risk","institutional_flow","options","system","agent_failure","data_source")
    severity: Enum("info","warning","critical")
    symbol: str | null
    message: str
    trigger_data: JSON
    status: Enum("active","acknowledged","resolved")
    delivery_status: Enum("pending","delivered","failed")
    created_at: datetime
    resolved_at: datetime | null

### SystemMetrics / APIHealth / DataSourceHealth / AuditLogs / ApplicationLogs
# (standard monitoring tables — see Section 18)
```

### 10.3 Parquet File Organization

```
data/market_data/
├── ohlcv/
│   ├── AAPL/
│   │   ├── daily.parquet           — Columns: date, open, high, low, close, volume, vwap
│   │   ├── weekly.parquet
│   │   └── monthly.parquet
│   ├── SPY/
│   ├── GLD/
│   ├── GC=F/                       — Gold futures
│   └── ... (all symbols)
├── options/
│   └── {symbol}/{date}.parquet     — Full options chain snapshot
└── features/
    └── {symbol}/feature_matrix.parquet  — ML feature store
```

**Parquet Write Strategy:** Append-only daily updates. Each symbol's daily.parquet is read into pandas DataFrame, new row appended, written back. Weekly/monthly computed on Sunday night and month-end from daily data.

### 10.4 diskcache Key Design

```
Cache key convention: "{namespace}:{identifier}:{variant}"

Examples:
  "ohlcv:AAPL:daily"              TTL: 3600s (1 hour)
  "prediction:AAPL:10d"           TTL: 1800s (30 min)
  "agent_output:22:AAPL"          TTL: 1800s
  "explanation:pred_{uuid}"       TTL: 86400s (24 hours)
  "news:AAPL"                     TTL: 1800s
  "symbol_search:aapl"            TTL: 3600s
  "alpha_vantage:quote:AAPL"      TTL: 300s (rate limit guard)
  "fred:GDP"                      TTL: 86400s
  "rate_limit:alpha_vantage"      TTL: 86400s (request counter)
```

### 10.5 Index Strategy (SQLite)

```sql
CREATE INDEX idx_agent_outputs_symbol ON agent_outputs(symbol, created_at);
CREATE INDEX idx_predictions_symbol ON predictions(symbol, horizon_days, prediction_date);
CREATE INDEX idx_predictions_status ON predictions(status, expiry_date);
CREATE INDEX idx_signals_symbol ON signals(symbol, signal_type, created_at);
CREATE INDEX idx_news_articles_published ON news_articles(published_at DESC);
CREATE INDEX idx_news_sentiment_symbol ON news_sentiment(symbol, analyzed_at);
CREATE INDEX idx_alerts_status ON alerts(status, severity, created_at);
CREATE INDEX idx_insider_transactions_symbol ON insider_transactions(symbol, transaction_date);
CREATE UNIQUE INDEX idx_symbols_ticker ON symbols(ticker);
```

---

## 11. Market Data Architecture

### 11.1 Data Collection Layer

**DataCollectionLayer** is the abstraction over all external data sources. Each collector implements `CollectorBase`:

```python
class CollectorBase(ABC):
    source_name: str
    requires_api_key: bool
    daily_request_limit: int | None
    
    @abstractmethod
    def fetch(self, symbol: str, **kwargs) -> pd.DataFrame: pass
    
    def fetch_with_fallback(self, symbol: str, **kwargs) -> pd.DataFrame:
        """Try primary → secondary → fallback. Raises DataUnavailableError if all fail."""
```

**Collector Implementations:**
- `YahooFinanceCollector` — wraps `yfinance.download()` and `yfinance.Ticker()`; no API key
- `AlphaVantageCollector` — wraps Alpha Vantage REST API; `ALPHA_VANTAGE_API_KEY`; 25 req/day limit tracked via diskcache counter
- `StooqCollector` — wraps `pandas_datareader.DataReader('symbol', 'stooq')` ; no key
- `FREDCollector` — wraps FRED REST API; `FRED_API_KEY`; unlimited
- `SECEdgarCollector` — fetches 13F filings and Form 4 from SEC EDGAR; no key
- `FINRAATSCollector` — fetches weekly aggregate ATS data; no key
- `CBOECollector` — fetches options data and VIX from CBOE public pages; no key
- `NewsAPICollector` — wraps NewsAPI; `NEWS_API_KEY`; 100 req/day
- `EIACollector` — fetches petroleum and natural gas inventory reports; `EIA_API_KEY`; unlimited
- `NasdaqDataLinkCollector` — wraps Quandl/Nasdaq Data Link free tier; `NASDAQ_DATA_LINK_API_KEY`

### 11.2 Data Validation Layer

Every fetched DataFrame passes through `DataValidator`:
- **Price Reasonableness:** Current price within ±50% of previous close (flag for manual review if breached)
- **Volume Sanity:** Volume > 0 on any non-holiday trading day
- **Completeness:** Required columns (open, high, low, close, volume) all present
- **Timestamp Validity:** No future-dated records; no records older than 30 years
- **OHLC Logic:** High ≥ Open, High ≥ Close, Low ≤ Open, Low ≤ Close

Failed validation is logged to `data_quality` log. Partial failures (e.g. missing volume) are stored with `is_complete=False` flag.

### 11.3 Symbol Registry

At startup, `SymbolSearchService` loads `data/symbols/symbol_registry.json` into memory. This JSON file contains all tracked symbols:

```json
{
  "AAPL": {"name": "Apple Inc.", "type": "stock", "exchange": "NASDAQ", "sector": "Technology"},
  "SPY": {"name": "SPDR S&P 500 ETF Trust", "type": "etf", "exchange": "NYSE"},
  "GLD": {"name": "SPDR Gold Shares", "type": "etf", "exchange": "NYSE"},
  "GC=F": {"name": "Gold Futures", "type": "futures", "exchange": "CME"},
  "CL=F": {"name": "Crude Oil Futures", "type": "futures", "exchange": "NYMEX"},
  ...
}
```

Symbol registry is updated weekly from Yahoo Finance's available ticker lists.

### 11.4 Data Source to Agent Mapping

| Data Source | Agents That Use It |
|------------|-------------------|
| Yahoo Finance (OHLCV) | 1, 2, 3, 4, 5, 6, 25, 27, 28, 29, 30, 40 |
| Alpha Vantage | 1, 2, 4, 14, 25 (backup OHLCV) |
| FRED | 11, 12, 13, 14 |
| CBOE (VIX data) | 21, 22, 24, 26, 34 |
| Yahoo Finance (Options) | 21, 22, 34 |
| SEC EDGAR (13F) | 17 |
| SEC EDGAR (Form 4) | 19 |
| FINRA ATS | 16 (degraded) |
| NewsAPI | 7, 8, 9, 10 |
| Yahoo Finance News | 7, 8, 9 |
| FRED (Fed data) | 12 |
| Federal Reserve RSS | 12 |
| Yahoo Finance (ETF flows) | 20 |
| EIA | 35, 37 |
| Nasdaq Data Link | 35, 36, 37, 38, 39, 42 |
| Yahoo Finance (Commodities: GC=F, CL=F, etc.) | 35, 36, 37, 38, 39, 40, 41, 42 |

---

## 12. Agent Architecture (42 Agents)

### 12.1 Agent ID Reference Table

| ID | Name | Category | Tier | Refresh | Dependencies |
|----|------|----------|------|---------|-------------|
| 1 | Regime Detection | Direction | 1 | 15 min | None |
| 2 | Trend Structure | Direction | 1 | 15 min | None |
| 3 | Market Breadth | Direction | 1 | 15 min | None |
| 4 | Market Momentum | Direction | 1 | 15 min | None |
| 5 | Trend Following | Direction | 1 | 15 min | 2 |
| 6 | HMM Market State | Direction | 2 | Hourly | 1, 2 |
| 7 | News Analyst | News & Macro | 1 | 30 min | None |
| 8 | Earnings Sentiment | News & Macro | 1 | Daily | None |
| 9 | Event Detection | News & Macro | 1 | 30 min | 7 |
| 10 | Macro News Impact | News & Macro | 1 | 30 min | 7, 11 |
| 11 | Macro Analyst | News & Macro | 1 | Daily | None |
| 12 | Federal Reserve | News & Macro | 1 | Daily | 11 |
| 13 | Global Liquidity | News & Macro | 2 | Daily | 14 |
| 14 | Dollar Strength | News & Macro | 1 | Hourly | None |
| 15 | Sector Rotation | Institutional | 1 | Daily | 3, 20 |
| 16 | Dark Pool Flow | Institutional | 2 | Daily | None (DEGRADED in MVP) |
| 17 | 13F Institutional Accumulation | Institutional | 1 | Weekly | None |
| 18 | Whale Options Flow | Institutional | 2 | Daily | 21, 22 |
| 19 | Insider Transactions | Institutional | 1 | Daily | None |
| 20 | ETF Flow Intelligence | Institutional | 1 | Daily | None |
| 21 | Put Call Parity | Strength | 1 | Hourly | None |
| 22 | Gamma Exposure | Strength | 1 | Hourly | None |
| 23 | Factor Crowding | Strength | 2 | Daily | 15, 17 |
| 24 | Uncertainty | Strength | 1 | Hourly | 26 |
| 25 | Relative Strength | Strength | 1 | Daily | 1, 2 |
| 26 | VIX Structure | Strength | 1 | Hourly | None |
| 27 | Correlation Decay | Exit & Reversal | 2 | Daily | 28 |
| 28 | Cross Asset Correlation | Exit & Reversal | 1 | Daily | 14, 26 |
| 29 | Market Leadership | Exit & Reversal | 1 | Daily | 3, 15 |
| 30 | Signal Aggregation | Prediction Layer | 1 | Per run | 1–29, 34–42 |
| 31 | Ensemble Model | Prediction Layer | 1 | Per run | 30 |
| 32 | Confidence Scoring | Prediction Layer | 1 | Per run | 30, 31 |
| 33 | Final Prediction Engine | Prediction Layer | 1 | Per run | 30, 31, 32 |
| 34 | Options OI Structure | Additional | 1 | Hourly | None |
| 35 | Crude Oil Intelligence | Commodity | 1 | Daily | None |
| 36 | Gold & Precious Metals | Commodity | 1 | Daily | None |
| 37 | Natural Gas Intelligence | Commodity | 1 | Daily | None |
| 38 | Silver Intelligence | Commodity | 1 | Daily | None |
| 39 | Copper Intelligence | Commodity | 1 | Daily | None |
| 40 | Commodity Momentum | Commodity | 1 | Daily | 35–39 |
| 41 | Commodity Sentiment | Commodity | 2 | Daily | 7 |
| 42 | Commodity Flow & Positioning | Commodity | 2 | Daily | 20, 40 |

### 12.2 Agent Detailed Specifications

---

#### Agent 1 — Regime Detection
**Purpose:** Classify current market regime as Trending-Up, Trending-Down, Range-Bound, Volatile, or Transitional.  
**Inputs:** Daily OHLCV (SPY + target symbol), ADX, ATR, rolling volatility  
**Key Calculations:**
- ADX > 25 → Trending; ADX < 20 → Range-Bound
- 20-day realized volatility vs 60-day realized volatility (ratio > 1.3 → Volatile)
- HMM state probability from Agent 6 (when available)
- Regime score: 0–100 (100 = strong trend up, 50 = neutral, 0 = strong trend down)
**Outputs:** regime_label, regime_score, adx_value, volatility_ratio  
**Data Sources:** Yahoo Finance OHLCV (primary), Alpha Vantage (fallback)  
**LLM-Ready Summary Example:** `{"agent": "Regime Detection", "signal": "Bullish", "finding": "ADX at 34.2 confirms strong uptrend; regime_score=78; volatility ratio=0.9 (stable)"}`

---

#### Agent 2 — Trend Structure
**Purpose:** Identify trend direction, strength, and structure using multiple moving average systems.  
**Inputs:** Daily OHLCV  
**Key Calculations:**
- EMA 8 / EMA 21 / EMA 50 / EMA 200 alignment
- Price relative to EMA200 (bullish if above, bearish if below)
- Golden Cross / Death Cross detection (EMA50 vs EMA200)
- Trend slope (linear regression over 20 days)
**Outputs:** trend_direction, ema_alignment_score, golden_cross (bool), price_above_ema200 (bool)  
**Data Sources:** Yahoo Finance OHLCV

---

#### Agent 3 — Market Breadth
**Purpose:** Measure participation of the broader market in the current trend.  
**Inputs:** S&P 500 constituent OHLCV data (sampled 100 largest)  
**Key Calculations:**
- % of S&P 500 stocks above 20-day MA
- % of S&P 500 stocks above 50-day MA
- % of S&P 500 stocks above 200-day MA
- Advance-Decline ratio (approximated from index ETF data)
- Breadth Score = weighted average of above metrics (0–100)
**Outputs:** breadth_score, pct_above_20d, pct_above_50d, pct_above_200d  
**Data Sources:** Yahoo Finance (SPY constituent proxies via ETF sector data)

---

#### Agent 4 — Market Momentum
**Purpose:** Measure the strength and direction of price momentum across multiple timeframes.  
**Inputs:** Daily OHLCV  
**Key Calculations:**
- RSI (14) — overbought (>70), oversold (<30)
- MACD (12/26/9) — signal line crossover
- Rate of Change (ROC) over 10, 20, 60 days
- Stochastic %K/%D
- Momentum Score = composite of above indicators (0–100)
**Outputs:** momentum_score, rsi_14, macd_signal, roc_10, roc_20  
**Data Sources:** Yahoo Finance OHLCV

---

#### Agent 5 — Trend Following
**Purpose:** Generate trend-following signals using breakout and channel systems.  
**Inputs:** Daily OHLCV, Agent 2 (Trend Structure)  
**Key Calculations:**
- Donchian Channel (20-day): price above upper channel = bullish breakout
- Keltner Channel deviation
- 52-week high/low proximity
- Volume confirmation of breakouts (breakout volume > 1.5x 20-day avg volume)
**Outputs:** breakout_signal, channel_position, volume_confirmation  
**Data Sources:** Yahoo Finance OHLCV

---

#### Agent 6 — HMM Market State
**Purpose:** Use a Hidden Markov Model to probabilistically classify market states.  
**Inputs:** Daily returns, volatility series, Agent 1 (Regime), Agent 2 (Trend)  
**Key Calculations:**
- 3-state HMM: Bull, Bear, Sideways (trained offline, updated weekly)
- Forward algorithm for current state probability
- State transition probability
**Outputs:** hmm_state, bull_probability, bear_probability, sideways_probability  
**Tier:** 2 (Production) — MVP uses simplified rule-based state machine as placeholder  
**Data Sources:** Derived from Yahoo Finance OHLCV

---

#### Agent 7 — News Analyst
**Purpose:** Collect and score news sentiment for the target symbol.  
**Inputs:** Latest 50 news articles for the symbol (24-hour window)  
**Key Calculations:**
- VADER sentiment scoring per headline
- TextBlob polarity as secondary scorer
- Composite sentiment = average weighted by article recency
- Bullish/Bearish article ratio
**Outputs:** news_sentiment_score, bullish_article_count, bearish_article_count, top_headline  
**Data Sources:** NewsAPI (primary), Yahoo Finance News (fallback)

---

#### Agent 8 — Earnings Sentiment
**Purpose:** Analyze earnings event proximity and earnings surprise history.  
**Inputs:** Earnings calendar data, earnings surprise history  
**Key Calculations:**
- Days until next earnings event
- Last 4 quarters earnings surprise average (beat/miss magnitude)
- Post-earnings drift (average 5-day return post-earnings)
- Risk premium for upcoming earnings (reduces confidence)
**Outputs:** earnings_risk_score, days_to_earnings, surprise_average, post_earnings_drift  
**Data Sources:** Yahoo Finance earnings data, Alpha Vantage earnings endpoint

---

#### Agent 9 — Event Detection
**Purpose:** Detect high-impact macro events and flag prediction risk.  
**Inputs:** Economic calendar, Fed calendar, news articles (Agent 7)  
**Key Calculations:**
- Event proximity score: CPI/PPI/GDP/FOMC within 3 days → high risk flag
- Event impact history: average market move on similar past events
**Outputs:** event_risk_score, next_event_name, next_event_date, historical_impact  
**Data Sources:** FRED calendar, Federal Reserve RSS, Yahoo Finance

---

#### Agent 10 — Macro News Impact
**Purpose:** Score the market impact of recent macro news headlines.  
**Inputs:** Agent 7 (News), Agent 11 (Macro Analyst)  
**Key Calculations:**
- NLP keyword extraction for macro themes (inflation, recession, rate hike, etc.)
- Theme impact scoring based on current regime context
- Macro news composite impact: -100 (very bearish) to +100 (very bullish)
**Outputs:** macro_news_impact_score, dominant_theme, theme_direction  
**Data Sources:** NewsAPI, Federal Reserve RSS feeds

---

#### Agent 11 — Macro Analyst
**Purpose:** Analyze macroeconomic indicators for market direction bias.  
**Inputs:** FRED economic series: CPI YoY, GDP growth rate, unemployment rate, M2 money supply  
**Key Calculations:**
- Yield curve slope (10Y minus 2Y Treasury spread)
- CPI trend (accelerating vs decelerating)
- Unemployment trend
- Composite Macro Score (0–100; 50 = neutral)
**Outputs:** macro_score, yield_curve_slope, cpi_yoy, unemployment_rate, m2_growth  
**Data Sources:** FRED API

---

#### Agent 12 — Federal Reserve
**Purpose:** Analyze Federal Reserve policy stance and communication tone.  
**Inputs:** FRED federal funds rate series, FOMC meeting minutes keywords  
**Key Calculations:**
- Current Fed Funds Rate vs neutral rate estimate
- Recent rate change direction (hiking/cutting/holding)
- FOMC minutes sentiment (hawkish vs dovish keywords)
- Fed pivot probability estimate
**Outputs:** fed_stance, fed_funds_rate, rate_direction, fomc_sentiment_score  
**Data Sources:** FRED API, Federal Reserve RSS feeds, Federal Reserve press release parsing

---

#### Agent 13 — Global Liquidity
**Purpose:** Track global liquidity conditions and their impact on US equities.  
**Inputs:** Agent 14 (Dollar Strength), Fed balance sheet data, M2 money supply  
**Key Calculations:**
- Fed balance sheet size trend (expanding vs contracting)
- Global M2 proxy (USD-adjusted)
- DXY trend impact on liquidity conditions
**Outputs:** liquidity_score, balance_sheet_direction, global_m2_trend  
**Tier:** 2 (Production)  
**Data Sources:** FRED API

---

#### Agent 14 — Dollar Strength
**Purpose:** Track DXY (US Dollar Index) and its directional influence on US equities and commodities.  
**Inputs:** DXY OHLCV, UUP ETF as proxy  
**Key Calculations:**
- DXY 20-day trend (rising = generally bearish for stocks/commodities)
- DXY relative to 200-day EMA
- DXY RSI (strength/weakness)
**Outputs:** dxy_signal, dxy_trend, dxy_rsi, dxy_vs_ema200  
**Data Sources:** Yahoo Finance (DX-Y.NYB or UUP ETF), Alpha Vantage

---

#### Agent 15 — Sector Rotation
**Purpose:** Identify money flows between S&P 500 sectors and the target symbol's sector positioning.  
**Inputs:** Sector ETF OHLCV (XLK, XLF, XLE, XLV, XLI, XLY, XLP, XLRE, XLU, XLB, XLC), Agent 3 (Breadth), Agent 20 (ETF Flows)  
**Key Calculations:**
- Relative sector performance (30-day return ranking)
- Sector flow momentum
- Determine if target symbol's sector is leading or lagging
**Outputs:** sector_rotation_score, sector_rank, sector_momentum, target_sector_bias  
**Data Sources:** Yahoo Finance (sector ETF OHLCV)

---

#### Agent 16 — Dark Pool Flow
**Purpose:** Track institutional off-exchange (dark pool) trading activity.  
**Inputs:** FINRA ATS weekly aggregate data  
**⚠️ MVP DEGRADED MODE:** FINRA ATS provides aggregate weekly data only. Agent 16 operates in degraded mode — produces a low-confidence signal based on weekly aggregate. Full functionality requires Unusual Whales or Ortex API (Production upgrade).  
**Key Calculations (Degraded):**
- Weekly ATS volume for target symbol relative to 4-week average
- Accumulation vs distribution inference from volume direction
**Outputs:** dark_pool_signal (low_confidence=True), accumulation_score, distribution_score, is_degraded=True  
**Data Sources:** FINRA ATS (free, aggregate)  
**Production Upgrade:** Unusual Whales API or Ortex

---

#### Agent 17 — 13F Institutional Accumulation
**Purpose:** Track institutional investor position changes from 13F quarterly filings.  
**Inputs:** SEC EDGAR 13F filing data  
**Key Calculations:**
- Top 50 institutional holders: position change vs. previous quarter
- Net institutional accumulation/distribution
- New positions opened vs closed
- Number of institutions increasing vs decreasing holdings
**Outputs:** institutional_accumulation_score, net_position_change_pct, institutions_buying, institutions_selling  
**Data Sources:** SEC EDGAR (no API key required)  
**Note:** Data is quarterly — score is frozen between filing dates

---

#### Agent 18 — Whale Options Flow
**Purpose:** Detect unusually large options activity that may signal institutional directional bets.  
**Inputs:** Options chain data, Agent 21 (Put/Call), Agent 22 (GEX)  
**Key Calculations:**
- Unusually large single options transactions vs 30-day average size
- Premium spent on calls vs puts (whale bias)
- OTM large call/put sweeps as directional signals
**Outputs:** whale_flow_signal, call_premium_ratio, put_premium_ratio, whale_bias_score  
**Tier:** 2 (Production)  
**Data Sources:** CBOE public data, Yahoo Finance options

---

#### Agent 19 — Insider Transactions
**Purpose:** Track SEC Form 4 insider buy/sell activity.  
**Inputs:** SEC EDGAR Form 4 filings  
**Key Calculations:**
- Insider purchases in last 30 days (strongly bullish signal)
- Insider sales in last 30 days (mildly bearish — may be tax/diversification)
- Net insider transaction value (buys minus sells)
- Number of unique insiders buying vs selling
**Outputs:** insider_signal, insider_buy_count, insider_sell_count, net_insider_value  
**Data Sources:** SEC EDGAR EFTS API (no key required)

---

#### Agent 20 — ETF Flow Intelligence
**Purpose:** Track ETF inflows and outflows for target symbol and relevant sector ETFs.  
**Inputs:** ETF OHLCV + AUM estimates, sector ETF flows  
**Key Calculations:**
- For ETFs: estimated daily creation/redemption unit activity (inferred from price/NAV spread)
- For stocks: flows in relevant sector ETF (XLK for tech, XLE for energy, etc.)
- ETF flow momentum score over 5-day, 10-day, 20-day windows
**Outputs:** etf_flow_score, inflow_trend, outflow_trend, sector_etf_flow  
**Data Sources:** Yahoo Finance (ETF OHLCV)

---

#### Agent 21 — Put/Call Parity
**Purpose:** Analyze options put/call ratios to gauge market sentiment and hedging activity.  
**Inputs:** Options chain data for target symbol  
**Key Calculations:**
- Put/Call Ratio by volume (< 0.7 = bullish, > 1.3 = bearish)
- Put/Call Ratio by open interest
- Skew: implied volatility of OTM puts vs OTM calls
- 20-day rolling Put/Call average (mean reversion signal)
**Outputs:** put_call_ratio, put_call_oi_ratio, iv_skew, sentiment_score  
**Data Sources:** CBOE (primary), Yahoo Finance options (fallback)

---

#### Agent 22 — Gamma Exposure
**Purpose:** Calculate dealer Gamma Exposure (GEX) to determine if market makers are amplifying or dampening price moves.  
**Inputs:** Options chain (strike, OI, calls/puts, spot price, IV, DTE)  
**Key Calculations:**
- GEX formula: Σ(Gamma × OI × 100 × Spot²) per strike, signed by dealer position
- Positive GEX: dealer long gamma → pins price, suppresses volatility
- Negative GEX: dealer short gamma → amplifies moves, increases volatility
- Key GEX levels: Call Wall (highest positive GEX strike), Put Wall, Zero Gamma level
**Outputs:** gex_value, gex_signal, call_wall, put_wall, zero_gamma_level, dealer_positioning  
**Data Sources:** CBOE, Yahoo Finance options

---

#### Agent 23 — Factor Crowding
**Purpose:** Detect when specific investment factors are overcrowded (high risk of unwind).  
**Inputs:** Agent 15 (Sector Rotation), Agent 17 (13F)  
**Key Calculations:**
- Factor exposure estimate (momentum, value, quality, low-vol)
- Crowding score based on institutional concentration in similar positions
- Crowding unwind risk (high crowding + deteriorating factor = reversal risk)
**Outputs:** crowding_score, dominant_factor, unwind_risk  
**Tier:** 2 (Production)  
**Data Sources:** Derived from Agent 15 and Agent 17 outputs

---

#### Agent 24 — Uncertainty
**Purpose:** Quantify prediction uncertainty from all uncertainty signals.  
**Inputs:** Agent 26 (VIX Structure), earnings calendar, Agent 9 (Event Detection)  
**Key Calculations:**
- Composite uncertainty score: VIX level + VIX term structure + upcoming events + earnings proximity
- High uncertainty (score > 70) penalizes final prediction confidence
**Outputs:** uncertainty_score, vix_contribution, event_contribution, earnings_contribution  
**Data Sources:** Derived from Agent 26 and Agent 9 outputs

---

#### Agent 25 — Relative Strength
**Purpose:** Compare target symbol's price performance against the S&P 500 and sector peers.  
**Inputs:** Target symbol OHLCV, SPY OHLCV, sector ETF OHLCV, Agent 1 (Regime), Agent 2 (Trend)  
**Key Calculations:**
- RS Ratio = symbol return / SPY return over 20, 60, 120 days
- RS Momentum = trend of RS Ratio
- Relative strength rank within sector
**Outputs:** rs_score, rs_ratio_20d, rs_ratio_60d, rs_momentum, sector_rank  
**Data Sources:** Yahoo Finance OHLCV

---

#### Agent 26 — VIX Structure
**Purpose:** Analyze VIX level, trend, and term structure for volatility risk assessment.  
**Inputs:** VIX, VIX9D, VIX3M daily data  
**Key Calculations:**
- VIX level zones: < 15 (calm), 15–20 (normal), 20–30 (elevated), > 30 (extreme)
- VIX term structure: contango (VIX9D < VIX3M = normal), backwardation (inverted = fear)
- VIX trend: rising VIX = bearish signal; falling VIX = bullish signal
- Fear/Complacency Score (0–100)
**Outputs:** vix_level, vix_structure, fear_score, volatility_regime  
**Data Sources:** CBOE (primary), Yahoo Finance (^VIX, ^VIX9D, ^VIX3M)

---

#### Agent 27 — Correlation Decay
**Purpose:** Detect weakening correlations between the target asset and its historical correlated peers (early reversal signal).  
**Inputs:** Agent 28 (Cross Asset Correlation) outputs  
**Key Calculations:**
- Rolling 20-day correlation between symbol and sector ETF
- Compare to 60-day baseline correlation
- Significant correlation drop (> 0.3 delta) = potential regime change / reversal signal
**Outputs:** correlation_decay_signal, current_correlation, baseline_correlation, decay_score  
**Tier:** 2 (Production)  
**Data Sources:** Derived from Agent 28

---

#### Agent 28 — Cross Asset Correlation
**Purpose:** Map cross-asset relationships (equity-commodity, equity-DXY, equity-rates) to identify macro regime shifts.  
**Inputs:** Target symbol OHLCV, gold (GLD), oil (USO), DXY (UUP), TLT (long bonds), Agent 14 (Dollar), Agent 26 (VIX)  
**Key Calculations:**
- 20-day correlation matrix between symbol and macro assets
- Risk-On / Risk-Off regime classification
- Identify if correlations are acting normally or breaking down
**Outputs:** cross_asset_regime, risk_on_score, correlation_matrix  
**Data Sources:** Yahoo Finance OHLCV

---

#### Agent 29 — Market Leadership
**Purpose:** Identify whether the target symbol or its sector is leading the market (strength) or lagging (weakness).  
**Inputs:** Agent 3 (Breadth), Agent 15 (Sector Rotation)  
**Key Calculations:**
- Sector leadership rank (1 = leading, 11 = lagging)
- Market cap breadth: large caps vs small caps leadership
- Symbol leadership within its sector
**Outputs:** leadership_score, sector_leadership_rank, symbol_vs_sector_rank  
**Data Sources:** Derived from Agent 3 and Agent 15

---

#### Agent 30 — Signal Aggregation
**Purpose:** Aggregate all agent outputs into a unified signal matrix. Critical dependency for Agents 31–33.  
**Inputs:** All outputs from Agents 1–29, 34–42  
**Key Calculations:**
- Collect all AgentOutput objects
- Apply tier weights: Tier 1 agents get full weight; Tier 2 agents get 0.7x weight; Tier 3 agents 0.5x
- Apply regime-based weight adjustments (e.g., VIX agent weight increases when VIX > 25)
- Apply category-based adjustments (commodity agents weighted up for commodity symbols)
- Build signal matrix: weighted bullish score, weighted bearish score, net direction score
- Compile top-5 bullish findings and top-5 bearish findings as `llm_ready_summary` JSON list for LLM prompt
**Outputs:** signal_matrix, weighted_bull_score, weighted_bear_score, net_score, agent_consensus_rate, llm_findings_package

---

#### Agent 31 — Ensemble Model
**Purpose:** Run ML ensemble models against agent feature outputs to generate directional probability predictions.  
**Inputs:** Agent 30 signal matrix (used as feature vector)  
**Key Calculations:**
- Feature vector: all 42 agent scores + Tier 2 cross-agent features
- Run LightGBM, XGBoost, Random Forest, Logistic Regression, CatBoost, Extra Trees
- Ensemble probability averaging per direction (Bullish / Bearish / Neutral)
- Per-horizon model (6 separate models: 2D, 5D, 10D, 20D, 30D, 60D)
**Outputs:** per-horizon: direction_probability (Bullish, Bearish, Neutral), ensemble_agreement_score  
**Data Sources:** Offline-trained models loaded from `ml/artifacts/`

---

#### Agent 32 — Confidence Scoring
**Purpose:** Calculate a reliable, calibrated confidence score for each prediction.  
**Inputs:** Agent 30 signal matrix, Agent 31 ensemble probabilities  
**Key Calculations:**
- Base confidence = max(bullish_prob, bearish_prob) × 100
- Adjustment factors:
  - Agent consensus rate (higher consensus → +confidence)
  - Number of failed agents (each failed agent → -2 confidence)
  - VIX level (high VIX → -confidence)
  - Upcoming events (near FOMC/CPI → -confidence)
  - Historical model accuracy for horizon (higher accuracy → +confidence)
- Final confidence: clipped to 0–100
**Outputs:** per-horizon: confidence_score, confidence_components_breakdown

---

#### Agent 33 — Final Prediction Engine
**Purpose:** Combine all upstream outputs into the authoritative final prediction object for all 6 horizons.  
**Inputs:** Agents 30, 31, 32  
**Key Calculations:**
- Direction: argmax of ensemble probabilities from Agent 31
- Confidence: Agent 32 output
- Risk Score: 100 − confidence + VIX contribution + event risk (capped 0–100)
- Expected Move: regime-based historical ATR scaling × direction × horizon multiplier
- Compile prediction contributors (top-N agents by impact weight)
- **Trigger ExplainabilityEngine** (async background task — fires immediately after this agent completes)
**Outputs:** For each horizon: Prediction object (direction, confidence, risk_score, expected_move_pct, prediction_reasons, contributors)

---

#### Agent 34 — Options OI Structure
**Purpose:** Analyze the full options open interest structure to identify key support/resistance levels and dealer positioning.  
**Inputs:** Full options chain OI data by strike and expiry  
**Key Calculations:**
- Build OI profile across all strikes and expirations
- Identify max pain level
- Identify Call Wall (strike with highest OI calls) and Put Wall (strike with highest OI puts)
- Dealer delta position estimate
**Outputs:** oi_structure_score, max_pain, call_wall, put_wall, dealer_delta  
**Data Sources:** CBOE, Yahoo Finance options

---

#### Agent 35 — Crude Oil Intelligence
**Purpose:** Analyze crude oil market fundamentals, technicals, and supply/demand for CL/USO signals.  
**Inputs:** CL=F / USO OHLCV, EIA Weekly Petroleum Status Report (crude inventories), OPEC news  
**Key Calculations:**
- EIA inventory change vs expected (draw = bullish, build = bearish)
- Crude price vs 20/50/200-day EMA
- WTI-Brent spread
- OPEC production signal (NewsAPI keyword extraction)
**Outputs:** crude_signal, inventory_change, eia_impact, crude_trend  
**Data Sources:** EIA API (primary), Yahoo Finance (CL=F, USO), NewsAPI

---

#### Agent 36 — Gold & Precious Metals Intelligence
**Purpose:** Analyze gold market dynamics for GC/GLD signals.  
**Inputs:** GC=F / GLD OHLCV, Agent 14 (DXY), Agent 26 (VIX), FRED real interest rates  
**Key Calculations:**
- Gold vs DXY inverse relationship score
- Gold vs real rates relationship (TIPS yield proxy)
- Institutional open interest trend (Nasdaq Data Link COT data if available)
- Safe-haven demand score (VIX + macro uncertainty)
**Outputs:** gold_signal, dxy_inverse_score, real_rate_impact, safe_haven_score  
**Data Sources:** Yahoo Finance (GC=F, GLD), FRED, Nasdaq Data Link

---

#### Agent 37 — Natural Gas Intelligence
**Purpose:** Analyze natural gas supply/demand for NG/UNG signals.  
**Inputs:** NG=F / UNG OHLCV, EIA Natural Gas Storage Report  
**Key Calculations:**
- EIA storage change vs consensus estimate
- 5-year average seasonal pattern comparison
- Degree-day weather demand proxy
**Outputs:** natgas_signal, storage_change, seasonal_deviation, weather_demand_score  
**Data Sources:** EIA API, Yahoo Finance (NG=F, UNG)

---

#### Agent 38 — Silver Intelligence
**Purpose:** Analyze silver dynamics including industrial demand component.  
**Inputs:** SI=F / SLV OHLCV, Agent 36 (Gold), Agent 14 (DXY)  
**Key Calculations:**
- Gold-Silver ratio (high ratio = silver undervalued vs gold)
- Industrial demand proxy (copper correlation)
- Silver trend vs gold trend divergence
**Outputs:** silver_signal, gold_silver_ratio, industrial_demand_score  
**Data Sources:** Yahoo Finance (SI=F, SLV), Nasdaq Data Link

---

#### Agent 39 — Copper Intelligence
**Purpose:** Track copper as a leading economic indicator ("Dr. Copper") for broad market directional bias.  
**Inputs:** HG=F / CPER OHLCV, China PMI news sentiment (NewsAPI)  
**Key Calculations:**
- Copper price trend (leading indicator for economic growth expectations)
- Copper vs S&P 500 divergence (copper leading/lagging)
- China demand proxy (PMI news sentiment)
**Outputs:** copper_signal, economic_signal, china_demand_score  
**Data Sources:** Yahoo Finance (HG=F, CPER), NewsAPI

---

#### Agent 40 — Commodity Momentum
**Purpose:** Aggregate momentum signals across all commodity markets.  
**Inputs:** Agents 35–39 outputs  
**Key Calculations:**
- Composite commodity momentum score (average of commodity agent scores)
- Commodity cycle phase (reflation/deflation)
- Commodity vs equity relative performance
**Outputs:** commodity_momentum_score, commodity_cycle_phase  
**Data Sources:** Derived from Agents 35–39

---

#### Agent 41 — Commodity Sentiment
**Purpose:** Score news and analyst sentiment for commodity markets.  
**Inputs:** Agent 7 (News) outputs filtered for commodity keywords  
**Key Calculations:**
- Commodity-specific news sentiment scoring
- Supply shock and demand shock event detection
**Outputs:** commodity_sentiment_score, top_commodity_news  
**Tier:** 2 (Production)  
**Data Sources:** Derived from Agent 7

---

#### Agent 42 — Commodity Flow & Positioning
**Purpose:** Track institutional positioning in commodity markets via COT-style analysis.  
**Inputs:** Agent 20 (ETF Flows), Agent 40 (Commodity Momentum)  
**Key Calculations:**
- Commodity ETF flows (GLD, USO, SLV, UNG, CPER inflows/outflows)
- Net positioning trend
**Outputs:** commodity_flow_score, net_positioning_signal  
**Tier:** 2 (Production)  
**Data Sources:** Yahoo Finance (ETF OHLCV), Nasdaq Data Link

---

### 12.3 Agent Dependency Graph

```
Layer 1 (Parallel — no dependencies):
  [1][2][3][4] [7][8] [11] [14] [19] [20] [21][22][26] [34]
  [35][36][37][38][39]

Layer 2 (Parallel — depends on Layer 1):
  [5(←2)] [6(←1,2)] [9(←7)] [10(←7,11)] [12(←11)] [13(←14)]
  [15(←3,20)] [16] [17] [18(←21,22)] [23(←15,17)]
  [24(←26)] [25(←1,2)] [27] [28(←14,26)] [29(←3,15)]
  [40(←35-39)] [41(←7)] [42(←20,40)]

Layer 3 (Parallel — depends on Layer 2):
  [27(←28)]

Layer 4 (Sequential — Prediction Pipeline):
  30(←all above) → 31(←30) → 32(←30,31) → 33(←30,31,32)
```

---

## 13. Prediction Engine Architecture

### 13.1 Signal Aggregation (Agent 30)

**Weight System:**

Base weights are defined per agent in `AgentDefinitions.default_weight`. Dynamic adjustments:

| Condition | Weight Adjustment |
|-----------|------------------|
| VIX > 25 | Agent 26 weight × 1.5 |
| Earnings within 3 days | Agent 8 weight × 1.5, overall confidence −15 |
| FOMC within 1 day | Agent 12 weight × 2.0, overall confidence −20 |
| Commodity symbol (CL, GC, NG, etc.) | Agents 35–42 weight × 1.8 |
| Agent in FAILED status | Weight = 0, confidence penalty −2 per failed agent |
| Tier 2 agent | Weight × 0.7 |
| Tier 3 agent | Weight × 0.5 |

**Net Direction Score:**
```
bull_score = Σ(agent_score × agent_weight) for agents with Bullish signal
bear_score = Σ(agent_score × agent_weight) for agents with Bearish signal
neutral_score = Σ(agent_score × agent_weight) for agents with Neutral signal
total_weight = Σ(all agent_weights)
net_bull_pct = bull_score / total_weight  → 0–100
net_bear_pct = bear_score / total_weight  → 0–100
```

### 13.2 Ensemble Model (Agent 31)

Six separate ML models, one per prediction horizon (2D, 5D, 10D, 20D, 30D, 60D). Each model is a stacking ensemble:

- **Base Layer:** LightGBM, XGBoost, CatBoost, Random Forest, Extra Trees, Logistic Regression
- **Meta Layer:** Logistic Regression (trained on base model outputs as features)
- **Output:** Probability distribution over (Bullish, Bearish, Neutral) — sums to 1.0

### 13.3 Confidence Calculation (Agent 32)

```python
base_confidence = max(bullish_prob, bearish_prob) * 100

adjustments = {
    "agent_consensus_bonus": (consensus_rate - 0.5) * 20,   # +0 to +10
    "failed_agent_penalty": -2 * len(failed_agents),
    "high_vix_penalty": -max(0, (vix - 20) * 0.5),
    "event_proximity_penalty": -event_risk_score * 0.2,
    "historical_accuracy_bonus": (model_accuracy_30d - 0.5) * 30,  # +0 to +15
}

final_confidence = clip(base_confidence + sum(adjustments.values()), 0, 100)
```

### 13.4 Risk Score Calculation

```python
risk_components = {
    "volatility": vix_fear_score * 0.30,
    "event_risk": event_risk_score * 0.25,
    "model_uncertainty": (100 - confidence_score) * 0.20,
    "inverse_breadth": (100 - breadth_score) * 0.15,
    "failed_agents": min(30, len(failed_agents) * 3),
}
risk_score = clip(sum(risk_components.values()), 0, 100)
```

### 13.5 Expected Move Calculation

```python
horizon_atr_multipliers = {2: 0.5, 5: 1.0, 10: 1.8, 20: 2.5, 30: 3.5, 60: 5.0}
base_expected_move = atr_20d / current_price * 100  # as percentage
expected_move_pct = base_expected_move * horizon_atr_multipliers[horizon]
# Apply direction sign
if direction == "Bullish": expected_move_pct = +abs(expected_move_pct)
elif direction == "Bearish": expected_move_pct = -abs(expected_move_pct)
```

---

## 14. Explainability Engine & LLM Narrative System

### 14.1 Architecture Overview

The Explainability Engine has two components:
1. **Attribution Component** — computes structured agent attribution (always runs synchronously)
2. **LLM Narrative Component** — generates natural-language explanation (runs asynchronously)

### 14.2 Attribution Component (Synchronous)

Fires immediately after Agent 33 completes. Computes:
- Top 5 agents by contribution magnitude (impact weight × score delta from neutral)
- Top 5 bullish factors (from contributing agents' `bullish_factors` lists)
- Top 5 bearish factors (from contributing agents' `bearish_factors` lists)
- Per-agent contribution percentage
- SHAP-style feature importance from ensemble model outputs

### 14.3 LLM Narrative Component (Asynchronous)

**Trigger:** Agent 33 completion event → async background task (FastAPI `BackgroundTasks`)  
**SLA:** Narrative available within 10 seconds of prediction generation (typical Grok API latency < 3s)  
**Delivery to Frontend:** WebSocket push on channel `explanation_ready` with `prediction_id`

#### 14.3.1 ExplanationPromptBuilder

Assembles a structured prompt from prediction context:

```python
def build_prompt(self, context: ExplanationContext) -> str:
    return f"""You are a senior equity and commodity analyst at an institutional investment firm.

Write a 3-5 sentence market analysis explaining WHY the following asset is predicted to move in the indicated direction. 
Be specific. Use exact numbers. Do not be generic. Reference the actual data values provided.
Professional tone. No hedging phrases like "it is possible that" — state findings directly.

ASSET: {context.symbol} ({context.asset_name}) | Type: {context.asset_type}
CURRENT PRICE: ${context.current_price:.2f} | 52W Range: ${context.week52_low:.2f}–${context.week52_high:.2f}
PREDICTION: {context.direction} | Confidence: {context.confidence:.0f}/100 | Risk Score: {context.risk_score:.0f}/100
EXPECTED MOVE: {context.expected_move_pct:+.1f}% over {context.horizon_days} days
MARKET REGIME: {context.regime_label} (Agent 1 score: {context.regime_score:.0f})
VIX: {context.vix_level:.1f} | Structure: {context.vix_structure}
LATEST MACRO: {context.macro_summary}

TOP BULLISH SIGNALS:
{chr(10).join([f"- {f['agent']}: {f['finding']}" for f in context.top_bullish_factors[:5]])}

TOP BEARISH RISKS:
{chr(10).join([f"- {f['agent']}: {f['finding']}" for f in context.top_bearish_factors[:3]])}

TOP CONTRIBUTING AGENTS: {', '.join([f"{a['name']} ({a['score']:.0f})" for a in context.top_agents[:3]])}
{f"COMMODITY CONTEXT: {context.commodity_context}" if context.commodity_context else ""}
{f"LATEST NEWS: {context.top_headline}" if context.top_headline else ""}

Write the 3-5 sentence analysis now:"""
```

#### 14.3.2 LLM API Call

```python
# backend/modules/explainability/llm_client.py

import httpx
import os

async def generate_explanation(prompt: str) -> str:
    """Call Grok API to generate analyst narrative."""
    api_key = os.environ["GROK_API_KEY"]
    
    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.post(
            "https://api.x.ai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "content-type": "application/json",
            },
            json={
                "model": "grok-3-mini",
                "max_tokens": 400,
                "temperature": 0.3,
                "messages": [{"role": "user", "content": prompt}]
            }
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]
```

**Cost:** Free tier available via xAI — effectively $0 for MVP volumes (< 1,000 predictions/day)

#### 14.3.3 Fallback Narrative Builder

If LLM call fails (network error, rate limit, API unavailable), `ExplanationFallbackBuilder` generates a deterministic template-based narrative from the structured agent data:

```python
def build_fallback(self, context: ExplanationContext) -> str:
    top_bullish = context.top_bullish_factors[0] if context.top_bullish_factors else None
    top_bearish = context.top_bearish_factors[0] if context.top_bearish_factors else None
    
    return (
        f"{context.symbol} is predicted {context.direction} over {context.horizon_days} days "
        f"with {context.confidence:.0f}% confidence (risk score: {context.risk_score:.0f}/100). "
        f"The market regime is currently {context.regime_label} (ADX: {context.regime_score:.0f}), "
        f"with VIX at {context.vix_level:.1f} ({context.vix_structure} term structure). "
        + (f"Primary bullish driver: {top_bullish['agent']} — {top_bullish['finding']}. " if top_bullish else "")
        + (f"Key risk: {top_bearish['agent']} — {top_bearish['finding']}." if top_bearish else "")
    )
```

#### 14.3.4 Explanation Storage

After generation (LLM or fallback), stored to `PredictionExplanations` table and cached in diskcache:
- Key: `"explanation:pred_{prediction_id}"`
- TTL: 86400 seconds (24 hours)

#### 14.3.5 Frontend ExplanationCard Component

Displays in the symbol detail panel under "AI Explanation":
```
┌─────────────────────────────────────────────────────────┐
│  🔍 Why This Move?                    [LLM] 2min ago    │
│  ─────────────────────────────────────────────────────  │
│  [Full analyst narrative text rendered here]            │
│                                                         │
│  Key Factors:                                           │
│  [Regime: Trending Up] [GEX: +$2.1B] [RSI: 68]        │
│                                         [Regenerate]    │
└─────────────────────────────────────────────────────────┘
```

---

## 15. Machine Learning Architecture

### 15.1 Feature Architecture

**Tier 1 — Market Features (from OHLCV):**
- returns_1d, returns_5d, returns_10d, returns_20d
- realized_vol_10d, realized_vol_20d, realized_vol_60d
- volume_ratio_20d (current volume / 20d avg volume)
- atr_20d (normalized by price)
- rsi_14, rsi_2
- macd_signal, macd_histogram
- price_vs_ema20, price_vs_ema50, price_vs_ema200
- adx_14, plus_di, minus_di

**Tier 2 — Agent Features (one feature per agent score, confidence, signal):**
- For each agent i (1–42): `agent_{i}_score`, `agent_{i}_confidence`, `agent_{i}_signal_encoded`
- signal encoding: Bullish=1, Neutral=0, Bearish=-1

**Tier 3 — Cross-Agent Features:**
- breadth_x_momentum: agent_3_score × agent_4_score
- vix_x_regime: agent_26_score × agent_1_score
- etf_flow_x_sector: agent_20_score × agent_15_score
- news_x_earnings: agent_7_score × agent_8_score
- commodity_momentum_x_gold: agent_40_score × agent_36_score

**Tier 4 — Historical Context Features:**
- prev_prediction_direction_encoded (was last prediction correct?)
- rolling_model_accuracy_20d
- prediction_streak (consecutive correct/incorrect)
- days_since_regime_change

**Total Feature Count:** ~170 features

### 15.2 Label Design

For each prediction horizon H (2, 5, 10, 20, 30, 60 days):
```python
future_return = (price_H_days_forward - price_today) / price_today

label = (
    "Bullish"  if future_return > +0.015  # > +1.5%
    "Bearish"  if future_return < -0.015  # < -1.5%
    "Neutral"  otherwise                  # between -1.5% and +1.5%
)
```

### 15.3 Training Pipeline

```
1. DataCollection: load Parquet OHLCV + SQLite agent outputs for training window (3 years)
2. FeatureEngineering: compute all Tier 1–4 features, forward-fill missing agent data
3. FeatureValidation: check for data leakage (no future data), NaN handling, outlier clipping
4. LabelGeneration: compute labels for each horizon
5. TimeSeriesSplit: Walk-Forward Validation with 252-day training window, 21-day test window
6. ModelTraining: train all 6 base models per horizon per fold
7. EnsembleStacking: train meta-model on base model OOF predictions
8. Evaluation: compute accuracy, precision, recall, F1, ROC-AUC per fold
9. ModelSelection: select best ensemble configuration per horizon
10. ModelRegistry: save to MLflow with metadata (training date, features, metrics)
11. ModelDeployment: update `ml/artifacts/{horizon}/ensemble_model.pkl` files loaded by Agent 31
```

**Validation Strategy:** Walk-Forward with expanding window. Never random train/test split (data leakage prevention).

### 15.4 Model Monitoring

- **Accuracy Drift:** Alert if 7-day rolling accuracy drops > 5% from baseline
- **Feature Drift:** Alert if mean feature value shifts > 2σ from training distribution
- **Prediction Distribution Drift:** Alert if bullish/bearish/neutral ratio shifts unexpectedly
- Drift checks run nightly via scheduled job, stored in `SystemMetrics` table

### 15.5 Retraining Strategy

| Retraining Type | Frequency | Trigger |
|----------------|-----------|---------|
| Full Retrain | Weekly (Saturday midnight) | Scheduled |
| Incremental Update | Daily (after-hours) | New day's data available |
| Emergency Retrain | On-demand | Accuracy drift alert |

---

## 16. API Architecture

### 16.1 REST API Endpoint Inventory

**Base URL:** `/api/v1`

**Authentication:**
```
POST   /auth/login                     — username + password → JWT access + refresh tokens
POST   /auth/logout                    — Revoke session
POST   /auth/refresh                   — Refresh access token using refresh token
GET    /auth/me                        — Current user profile
```

**Symbols & Market Data:**
```
GET    /symbols/search?q={query}       — Autocomplete symbol search
GET    /symbols/{symbol}               — Symbol metadata
GET    /market/ohlcv/{symbol}          — OHLCV data (params: timeframe, period)
GET    /market/indicators/{symbol}     — Technical indicators
GET    /market/regime                  — Current market regime
```

**Predictions:**
```
GET    /predictions                    — All active predictions (filterable)
GET    /predictions/{id}               — Single prediction detail
POST   /predictions/generate           — Trigger prediction generation for symbol
GET    /predictions/symbol/{symbol}    — All predictions for a symbol
GET    /predictions/horizon/{horizon}  — Predictions by horizon
```

**Agents:**
```
GET    /agents                         — All 42 agent definitions + current status
GET    /agents/{id}                    — Single agent definition
GET    /agents/{id}/output/{symbol}    — Latest agent output for symbol
GET    /agents/{id}/history            — Agent run history
POST   /agents/{id}/trigger            — Manually trigger agent run (Admin only)
```

**Signals:**
```
GET    /signals                        — All active signals (filterable)
GET    /signals/symbol/{symbol}        — Signals for symbol
```

**Explainability:**
```
GET    /explanations/{prediction_id}   — Fetch LLM narrative for prediction
GET    /explanations/symbol/{symbol}   — Latest explanation for symbol
POST   /explanations/regenerate/{id}   — Trigger fresh LLM explanation call
GET    /explanations/history/{symbol}  — Paginated explanation history
```

**Institutional:**
```
GET    /institutional/etf-flows        — ETF flow summary
GET    /institutional/insider/{symbol} — Insider transactions
GET    /institutional/13f/{symbol}     — 13F holdings
GET    /institutional/dark-pool/{symbol} — Dark pool activity
```

**Options:**
```
GET    /options/chain/{symbol}         — Options chain data
GET    /options/gex/{symbol}           — Gamma exposure
GET    /options/oi-structure/{symbol}  — OI structure (call wall, put wall, max pain)
GET    /options/vix                    — VIX data
```

**News:**
```
GET    /news                           — News feed (filterable by symbol, date)
GET    /news/sentiment/{symbol}        — Sentiment summary
GET    /news/economic-calendar         — Upcoming economic events
```

**Backtesting:**
```
POST   /backtests                      — Run new backtest
GET    /backtests/{id}                 — Backtest results
GET    /backtests/symbol/{symbol}      — Backtest history for symbol
```

**Performance:**
```
GET    /performance/accuracy           — Prediction accuracy metrics
GET    /performance/agents             — Agent performance rankings
GET    /performance/models             — ML model performance
```

**Alerts:**
```
GET    /alerts                         — Active alerts
POST   /alerts                         — Create alert rule
PUT    /alerts/{id}/acknowledge        — Acknowledge alert
```

**Admin:**
```
GET    /admin/system                   — System metrics
GET    /admin/agents/status            — All 42 agent health statuses
GET    /admin/data-sources             — Data source health
GET    /admin/api-health               — API endpoint health stats
GET    /admin/logs                     — Application logs (paginated)
GET    /admin/users                    — User list
POST   /admin/users                    — Create user
PUT    /admin/users/{id}               — Update user
DELETE /admin/users/{id}               — Deactivate user
GET    /admin/config                   — System configuration
PUT    /admin/config                   — Update configuration (Super Admin only)
```

### 16.2 WebSocket API

**Endpoint:** `ws://{host}/ws` (authenticated via JWT query param: `?token={jwt}`)

**Channels (subscribe via message `{"action": "subscribe", "channel": "channel_name"}`):**

| Channel | Payload | Frequency |
|---------|---------|-----------|
| `market_data` | `{symbol, price, change_pct, volume}` | On new data |
| `agent_updates` | `{agent_id, symbol, signal, score, timestamp}` | On agent completion |
| `prediction_updates` | `{prediction_id, symbol, direction, confidence, horizon}` | On new prediction |
| `explanation_ready` | `{prediction_id, symbol, narrative_text, factors}` | On LLM explanation complete |
| `alerts` | `{alert_id, type, severity, message}` | On new alert |
| `system_health` | `{cpu, ram, disk, agent_healthy_count, agent_failed_count}` | Every 30 sec |

### 16.3 API Response Standards

All API responses follow this envelope format:

```json
{
  "success": true,
  "data": { ... },
  "meta": {
    "request_id": "uuid",
    "timestamp": "ISO8601",
    "version": "1.0"
  },
  "pagination": {          // Only present for list endpoints
    "page": 1,
    "per_page": 20,
    "total": 150,
    "total_pages": 8
  }
}
```

Error responses:
```json
{
  "success": false,
  "error": {
    "code": "PREDICTION_NOT_FOUND",
    "message": "Prediction with ID xyz not found",
    "details": {}
  },
  "meta": { "request_id": "uuid", "timestamp": "ISO8601" }
}
```

---

## 17. Security Architecture

### 17.1 Authentication

**JWT Implementation:**
- Access token expiry: 15 minutes
- Refresh token expiry: 7 days
- Algorithm: HS256
- Secret: `JWT_SECRET_KEY` env var (minimum 32 characters, randomly generated)
- Claims: `sub` (user_id), `role`, `exp`, `iat`, `jti` (unique token ID)

**Token Storage (Frontend):**
- Access token: in-memory (Zustand store — NOT localStorage)
- Refresh token: HttpOnly cookie (secure flag in production)

### 17.2 RBAC Permission Matrix

| Endpoint Group | Viewer | Analyst | Admin | Super Admin |
|---------------|--------|---------|-------|-------------|
| Public predictions, signals, news | ✓ | ✓ | ✓ | ✓ |
| Symbol search + analysis | ✓ | ✓ | ✓ | ✓ |
| Backtesting | Read | Read+Write | Read+Write | Read+Write |
| Regenerate explanations | ✗ | ✓ | ✓ | ✓ |
| Trigger agent runs | ✗ | ✗ | ✓ | ✓ |
| Admin dashboard | ✗ | ✗ | ✓ | ✓ |
| User management | ✗ | ✗ | ✓ | ✓ |
| System configuration | ✗ | ✗ | ✗ | ✓ |
| API key management | ✗ | ✗ | ✗ | ✓ |

### 17.3 Rate Limiting

Implemented in FastAPI middleware using diskcache counters:

| Endpoint Group | Limit |
|---------------|-------|
| Auth (login) | 5 requests / 1 minute per IP |
| Symbol search | 30 requests / 1 minute per user |
| Prediction generation | 10 requests / 1 minute per user |
| Admin endpoints | 60 requests / 1 minute per user |
| All other endpoints | 120 requests / 1 minute per user |

### 17.4 Secrets Management

**Development:** `.env` file in project root (never committed; `.env.example` committed as template)  
**Production (Railway/Render):** Environment variables set via platform UI or CLI — never stored in code or Docker images  
**Enterprise:** HashiCorp Vault or AWS Secrets Manager

Required secrets:
```
ALPHA_VANTAGE_API_KEY
NEWS_API_KEY
FRED_API_KEY
NASDAQ_DATA_LINK_API_KEY
GROK_API_KEY
EIA_API_KEY
JWT_SECRET_KEY
DATABASE_URL            # Only needed when upgrading from SQLite to PostgreSQL
REDIS_URL               # Only needed when upgrading from diskcache to Redis
```

### 17.5 Input Validation

- All request bodies validated via Pydantic v2 schemas — automatic 422 on invalid input
- Symbol parameters sanitized: uppercase, alphanumeric + `=`, `-`, `.` only, max 20 characters
- SQL injection impossible via SQLAlchemy ORM (no raw SQL with user input)
- HTML/JS injection prevented by Pydantic string validators (strip tags)

### 17.6 Audit Logging

All write operations and admin actions logged to `AuditLogs` table:
```
Fields: id, user_id, action, resource_type, resource_id, old_value, new_value, ip_address, timestamp
```

---

## 18. Monitoring & Observability

### 18.1 Metrics (Prometheus)

Exposed at `/metrics` via `prometheus-fastapi-instrumentator`. Custom metrics:

```python
# Per-agent metrics
agent_execution_duration_seconds    # Histogram, labels: agent_id, symbol
agent_success_total                 # Counter, labels: agent_id
agent_failure_total                 # Counter, labels: agent_id, error_type

# Prediction metrics
prediction_generation_duration_seconds  # Histogram, labels: horizon
prediction_confidence_gauge             # Gauge, labels: symbol, horizon
prediction_accuracy_gauge               # Gauge (30d rolling), labels: horizon

# Data source metrics
data_source_request_total          # Counter, labels: source, status
data_source_latency_seconds        # Histogram, labels: source

# LLM explanation metrics
explanation_generation_total       # Counter, labels: status (success|fallback|failed)
explanation_latency_seconds        # Histogram

# System metrics
active_websocket_connections       # Gauge
cache_hit_rate                     # Gauge, labels: cache_key_namespace
```

### 18.2 Structured Logging

All logs are JSON formatted via `python-json-logger`. Log levels: DEBUG / INFO / WARNING / ERROR / CRITICAL.

**Log Schema:**
```json
{
  "timestamp": "2024-01-15T10:30:00.000Z",
  "level": "INFO",
  "logger": "agents.agent_22_gamma_exposure",
  "message": "Agent 22 completed for SPY",
  "agent_id": 22,
  "symbol": "SPY",
  "signal": "Bullish",
  "score": 74.2,
  "duration_ms": 342,
  "request_id": "uuid"
}
```

Log files written to `./logs/` directory, rotated daily, retained 30 days.

### 18.3 Health Check Endpoints

```
GET /health          — Returns 200 if service is up (no auth required)
GET /health/detailed — Returns status of all subsystems (auth required, admin)
```

Detailed health response:
```json
{
  "status": "healthy",
  "database": "healthy",
  "cache": "healthy",
  "agents": {"healthy": 40, "warning": 2, "failed": 0},
  "data_sources": {"yahoo_finance": "healthy", "alpha_vantage": "healthy", ...},
  "scheduler": "running",
  "last_prediction": "2024-01-15T10:00:00Z"
}
```

### 18.4 Alerting Thresholds

| Condition | Severity | Action |
|-----------|----------|--------|
| > 3 agents in FAILED status | Warning | Dashboard alert |
| > 10 agents in FAILED status | Critical | Dashboard alert + email |
| Prediction accuracy (7d) drops > 8% | Warning | Dashboard alert |
| LLM explanation fallback rate > 20% | Warning | Dashboard alert |
| Alpha Vantage daily limit > 90% used | Warning | Dashboard alert |
| NewsAPI daily limit > 90% used | Warning | Dashboard alert |
| API P99 response time > 2000ms | Warning | Log + dashboard alert |
| Disk usage > 80% | Warning | Dashboard alert |
| Any data source down > 30 min | Critical | Dashboard alert + email |

---

## 19. Deployment Architecture

### 19.1 Stage 1 — MVP Deployment

**Infrastructure:**
- Frontend: Vercel (free tier) — auto-deploy from `main` branch
- Backend: Railway (starter plan ~$5/month) or Render (free tier with spin-down limitation)
- Database: SQLite file stored on Railway/Render persistent disk
- Cache: diskcache directory on same persistent disk
- Market Data: Parquet files on same persistent disk

**Important:** Railway and Render provide persistent disk volumes. SQLite + diskcache files are stored there. Do not use ephemeral filesystem.

**Environment Variables:** Set via Railway/Render UI.

**MVP Deployment Steps:**
```
1. git clone repo
2. Set all .env variables in Railway/Render dashboard
3. Deploy backend: railway up (or render deploy)
4. Deploy frontend: vercel deploy
5. Run: alembic upgrade head (creates SQLite schema)
6. Run: python scripts/seed_symbol_registry.py (loads symbol_registry.json)
7. Run: python scripts/seed_agent_definitions.py (inserts 42 agent records)
8. System is live
```

**MVP Monthly Cost Estimate:**
| Service | Cost |
|---------|------|
| Vercel (frontend) | $0 |
| Railway / Render (backend) | $5–$10 |
| SQLite (no cloud DB) | $0 |
| diskcache (no Redis) | $0 |
| Free data APIs | $0 |
| Grok API (free tier) | $0 |
| **Total** | **~$5–$10/month** |

### 19.2 Stage 2 — Production Deployment

- Frontend: Vercel Pro
- Backend: Dedicated VPS (Hetzner CX31 ~$12/month) or Railway Pro
- Database: Managed PostgreSQL + TimescaleDB extension (Neon, Supabase, or Railway PostgreSQL)
- Cache: Managed Redis (Upstash free tier → paid, or Railway Redis)
- Monitoring: Grafana Cloud free tier + Prometheus
- Background jobs: Upgrade APScheduler → Celery with Redis broker

**SQLite → PostgreSQL Migration:**
1. Change `DATABASE_URL` env var: `postgresql://user:pass@host/dbname`
2. All SQLAlchemy models are compatible — same ORM code
3. Run `alembic upgrade head` on new PostgreSQL instance
4. Data migration: export SQLite to CSV, import to PostgreSQL

**Production Monthly Cost Estimate:**
| Service | Cost |
|---------|------|
| Vercel Pro | $20 |
| VPS / Railway Pro | $30–$50 |
| Managed PostgreSQL | $25 |
| Managed Redis | $15 |
| Grafana Cloud | $0 (free tier) |
| Grok API (xAI) | $0 |
| **Total** | **~$90–$115/month** |

### 19.3 Stage 3 — Enterprise Deployment

- Frontend: Vercel Enterprise
- Backend: AWS ECS (containers) or GCP Cloud Run
- Database: Aurora PostgreSQL with TimescaleDB
- Cache: ElastiCache Redis (Multi-AZ)
- Background: Celery workers on ECS/GKE
- Monitoring: Full Grafana + Prometheus stack, OpenTelemetry tracing, PagerDuty alerting
- CDN: CloudFront / Fastly
- Secrets: AWS Secrets Manager / HashiCorp Vault

### 19.4 CI/CD Pipeline (GitHub Actions)

```yaml
# .github/workflows/deploy.yml

on:
  push:
    branches: [main]

jobs:
  test:
    - pytest backend/tests/
    - npm test (frontend)
  
  deploy-backend:
    needs: test
    - Docker build + push to Railway / Render
    - alembic upgrade head
    - Smoke test: GET /health → 200
  
  deploy-frontend:
    needs: test
    - vercel deploy --prod
```

**Rollback Strategy:** Railway/Render maintain previous deployment. Rollback via platform UI in 30 seconds.

### 19.5 Environment Environments

| Environment | Branch | Database | Purpose |
|------------|--------|----------|---------|
| Development | local | SQLite (local file) | Local dev, full feature testing |
| Testing | CI | SQLite (in-memory) | Automated tests |
| Staging | staging | SQLite → PostgreSQL clone | Pre-production validation |
| Production | main | PostgreSQL | Live system |

### 19.6 Backup Strategy

**MVP:**
- SQLite file: daily copy to S3/Backblaze B2 (or Railway's built-in backup)
- Parquet files: weekly backup to S3

**Production:**
- PostgreSQL: automated daily snapshots via managed service
- Parquet files: daily S3 backup
- RTO: < 1 hour | RPO: < 24 hours

---

## 20. Cost Analysis

### 20.1 Data Source Cost Summary

| Source | MVP Cost | Production Cost | Notes |
|--------|----------|----------------|-------|
| Yahoo Finance (yfinance) | $0 | $0 | No key required |
| Alpha Vantage | $0 | $50/month | 25 req/day free; upgrade at scale |
| FRED | $0 | $0 | Always free |
| SEC EDGAR | $0 | $0 | Always free |
| FINRA ATS | $0 | $0 | Always free (aggregate) |
| CBOE | $0 | $0 | Public data always free |
| NewsAPI | $0 | $50/month | 100 req/day free; upgrade at scale |
| EIA | $0 | $0 | Always free |
| Nasdaq Data Link | $0 | $0 | Free tier sufficient for MVP |
| Unusual Whales (Dark Pool) | $0 (degraded) | $40/month | Production upgrade for Agent 16 |
| Grok API (xAI) | $0 | $0 | Free tier sufficient for MVP and production volumes |

### 20.2 Production Data Upgrade Path

When upgrading from free to paid data sources:

| Upgrade | Agents Improved | Expected Accuracy Improvement | Recommended Stage |
|---------|----------------|-------------------------------|------------------|
| Polygon.io ($29/mo) | 1,2,4,5,25 | +3–5% | Production |
| Unusual Whales ($40/mo) | 16,18 | +2–4% | Production |
| Alpha Vantage premium | 1,2,14,25 | +2% | Production |
| Barchart commodity data | 35,36,37,38,39 | +5% for commodity | Production |
| Databento ($50/mo) | 3,4,21,22 | +4% | Enterprise |
| Bloomberg API | All agents | +10–15% | Enterprise |

---

## 21. Risk Analysis

### 21.1 Technical Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
| Yahoo Finance API changes/breaks | Medium | High | Alpha Vantage + Stooq fallbacks; circuit breaker |
| SQLite performance limits at scale | High (at scale) | Medium | Documented upgrade path to PostgreSQL |
| ML model accuracy degradation | Medium | High | Drift monitoring + weekly retraining |
| LLM API downtime | Low | Low | Template fallback builder always available |
| APScheduler job failures | Low | Medium | Job status monitoring; missed job alerts |
| Parquet file corruption | Low | High | Daily backups; data reconstruction from API |

### 21.2 Data Risks

| Risk | Mitigation |
|------|-----------|
| Yahoo Finance rate limiting (unofficial API) | diskcache prevents redundant calls; Alpha Vantage fallback |
| Alpha Vantage 25 req/day limit | Aggressive caching (1hr TTL); request counter in diskcache |
| NewsAPI 100 req/day limit | Cache results 30min; batch queries per run |
| FINRA ATS aggregate-only data | Agent 16 operates in degraded mode with low confidence flag |
| SEC 13F data 45-day lag | Documented limitation; score adjusted for staleness |
| Stale commodity data (weekends/holidays) | Data freshness checks; weekend predictions flagged |

### 21.3 Model Risks

| Risk | Mitigation |
|------|-----------|
| Overfitting to training data | Walk-forward validation only; expanding window |
| Look-ahead bias | Strict temporal data splitting; no future data in features |
| Regime change invalidating model | Regime detection agent; model retraining triggered on regime shift |
| Low accuracy during market dislocations | Confidence penalized during high VIX + extreme events |

### 21.4 Operational Risks

| Risk | Mitigation |
|------|-----------|
| Single point of failure (monolith) | Health checks; Render/Railway auto-restart on crash |
| API key exposure | Environment variables only; never in code or logs |
| Large Parquet files degrading performance | Partition by symbol; index by date; regular compaction |
| Disk space exhaustion | Log rotation; Parquet compaction; alerts at 80% usage |

---

## 22. Scalability Strategy

### 22.1 MVP → Production Migration

| Component | MVP | Production | Migration Effort |
|-----------|-----|-----------|-----------------|
| Database | SQLite file | PostgreSQL + TimescaleDB | Change connection string; run Alembic migrations; data migration script |
| Cache | diskcache | Redis | Change cache backend in `core/cache.py` (CacheService abstraction); all callers unchanged |
| Background Jobs | APScheduler in-process | Celery + Redis broker | Extract agent jobs to Celery tasks; same function signatures |
| Frontend Deploy | Vercel free | Vercel Pro | No code changes |
| Backend Deploy | Railway/Render single instance | Multiple instances + load balancer | Stateless FastAPI; no code changes needed |

### 22.2 Production → Enterprise Migration

| Component | Production | Enterprise |
|-----------|-----------|-----------|
| Database | PostgreSQL | Aurora PostgreSQL (multi-AZ) + read replicas |
| Background | Celery | Celery + Kubernetes job pods |
| Cache | Redis | ElastiCache Redis Cluster |
| Data | Free APIs | Polygon + Bloomberg + Databento |
| Monitoring | Grafana Cloud | Full observability stack + OpenTelemetry |
| Auth | JWT | JWT + SSO (SAML/OIDC for enterprise clients) |

---

## 23. MVP Roadmap

### Phase 1 — Foundation (Weeks 1–2)
- [ ] Backend skeleton: FastAPI app, SQLAlchemy models, Alembic migrations, SQLite setup
- [ ] User auth module: login, JWT, RBAC
- [ ] Symbol registry: load and serve all US symbols
- [ ] Market data collector: Yahoo Finance OHLCV for major indices (SPY, QQQ, DIA, IWM)
- [ ] Data validation layer
- [ ] Basic health check endpoints
- [ ] Frontend skeleton: Next.js, Tailwind, ShadCN, auth screens

### Phase 2 — Core Agents (Weeks 3–4)
- [ ] Implement Tier 1 Direction Agents (1–5)
- [ ] Implement Tier 1 News & Macro Agents (7, 8, 11, 12, 14)
- [ ] Implement Tier 1 Institutional Agents (15, 17, 19, 20)
- [ ] Implement Tier 1 Strength Agents (21, 22, 24, 25, 26)
- [ ] Implement Exit & Reversal Agents (28, 29)
- [ ] Agent Engine: execution orchestration, dependency handling, failure isolation
- [ ] APScheduler: all Tier 1 agent jobs scheduled

### Phase 3 — Prediction Engine (Weeks 5–6)
- [ ] Signal Aggregation Agent (30)
- [ ] ML Training Pipeline: initial model training on 3 years of SPY data
- [ ] Ensemble Model Agent (31)
- [ ] Confidence Scoring Agent (32)
- [ ] Final Prediction Engine Agent (33)
- [ ] PredictionExplanations table + Attribution component
- [ ] LLM Narrative Engine (ExplanationPromptBuilder + Grok API client + fallback)
- [ ] WebSocket manager

### Phase 4 — Frontend Core (Weeks 7–8)
- [ ] Dashboard page: all widgets
- [ ] Global search bar + Symbol Detail Panel
- [ ] Predictions tab
- [ ] Agent Analysis tab (all 42 agents displayed)
- [ ] AI Explanations tab
- [ ] Basic admin panel (system health, agent monitoring)

### Phase 5 — Commodity & Additional Agents (Weeks 9–10)
- [ ] All Commodity Agents (35–42)
- [ ] Agent 34 (Options OI Structure)
- [ ] Commodity data collectors (EIA, Nasdaq Data Link)
- [ ] Commodity-specific frontend sections

### Phase 6 — Backtesting & Polish (Weeks 11–12)
- [ ] Backtesting Engine
- [ ] Performance Analytics
- [ ] Historical Predictions archive
- [ ] Alert Engine
- [ ] Full admin panel completion
- [ ] Mobile responsiveness pass
- [ ] Production deployment to Railway + Vercel

---

## 24. Production Roadmap

### Phase 1 — Stability & Data Quality
- [ ] Upgrade to PostgreSQL + TimescaleDB
- [ ] Upgrade to Redis
- [ ] Implement Celery for background jobs
- [ ] Implement Tier 2 agents (6, 13, 16, 18, 23, 27, 41, 42)
- [ ] Upgrade Agent 16 to Unusual Whales for real dark pool data
- [ ] Grafana + Prometheus monitoring stack
- [ ] OpenTelemetry distributed tracing

### Phase 2 — Intelligence Enhancement
- [ ] Add Polygon.io as primary OHLCV source
- [ ] Implement HMM Market State (Agent 6) properly
- [ ] Implement Factor Crowding (Agent 23) fully
- [ ] Add Barchart commodity data for Agents 35–39
- [ ] ML model weekly automated retraining pipeline
- [ ] Feature drift monitoring and alerting

### Phase 3 — Enterprise Features
- [ ] Multi-user organization accounts
- [ ] Custom alert webhooks
- [ ] Portfolio-level prediction aggregation
- [ ] API access for programmatic clients
- [ ] White-labeling support

---

## 25. Enterprise Roadmap

### Advanced AI
- [ ] Fine-tuned LLM for market analysis (trained on institutional research reports)
- [ ] Agent performance self-improvement via reinforcement learning from prediction outcomes
- [ ] Automated research report generation (PDF export of full analysis)

### Additional Markets
- [ ] International Equities: LSE, TSX, ASX, Nikkei, FTSE
- [ ] Crypto: BTC, ETH, top-50 tokens
- [ ] Forex: major pairs
- [ ] Fixed Income: Treasury yield curve prediction

### Multi-Asset Expansion
- [ ] Portfolio-level risk aggregation
- [ ] Cross-asset prediction correlation
- [ ] Custom universe definition per institutional client
- [ ] Bloomberg Terminal integration

---

## 26. Complete Folder Structure

```
usa-swing/
├── backend/                        — FastAPI backend (see Section 9.2 for full tree)
├── frontend/                       — Next.js frontend (see Section 7.8 for full tree)
├── ml/                             — Machine learning pipeline
│   ├── training/
│   ├── artifacts/
│   └── feature_store/
├── scripts/
│   ├── seed_symbol_registry.py     — Populate symbol_registry.json from Yahoo Finance
│   ├── seed_agent_definitions.py   — Insert 42 agent records into SQLite
│   ├── backfill_market_data.py     — Backfill 3 years of OHLCV for all symbols
│   ├── train_initial_models.py     — Train initial ML models (run once before MVP launch)
│   └── migrate_to_postgres.py      — SQLite → PostgreSQL migration script (production)
├── docs/
│   ├── SPEC.md                     — This document
│   ├── API.md                      — API reference (auto-generated from FastAPI)
│   └── AGENT_GUIDE.md              — Developer guide for adding new agents
├── .github/
│   └── workflows/
│       └── deploy.yml              — CI/CD pipeline
├── .env.example                    — Environment variable template
├── docker-compose.yml              — Optional: local dev with all services
└── README.md
```

---

## 27. Environment Configuration

### 27.1 Complete `.env.example`

```bash
# ============================================================
# USA Swing — Environment Configuration Template
# Copy to .env and fill in your values
# NEVER commit .env to version control
# ============================================================

# --- Application ---
APP_ENV=development                     # development | production | test
APP_SECRET_KEY=CHANGE_ME_32_CHARS_MIN   # Used for JWT signing — generate with: openssl rand -hex 32
DEBUG=true                              # Set to false in production

# --- Data APIs (Free — Register at listed URLs) ---
ALPHA_VANTAGE_API_KEY=your_key_here     # https://www.alphavantage.co/support/#api-key
NEWS_API_KEY=your_key_here              # https://newsapi.org/register
FRED_API_KEY=your_key_here             # https://fred.stlouisfed.org/docs/api/api_key.html
NASDAQ_DATA_LINK_API_KEY=your_key_here # https://data.nasdaq.com/sign-up
EIA_API_KEY=your_key_here              # https://www.eia.gov/opendata/register.php

# --- LLM API (xAI Grok — for explanation narratives) ---
GROK_API_KEY=your_key_here             # https://console.x.ai/

# --- Database (MVP: SQLite — no change needed) ---
DATABASE_URL=sqlite:///./data/usa_swing.db
SCHEDULER_DB_URL=sqlite:///./data/scheduler.db

# --- Cache (MVP: diskcache — no change needed) ---
CACHE_DIR=./data/cache
CACHE_DEFAULT_TTL=3600

# --- Storage ---
PARQUET_DATA_DIR=./data/market_data
LOG_DIR=./logs

# --- Production Upgrades (uncomment when migrating) ---
# DATABASE_URL=postgresql://user:pass@host:5432/usa_swing
# REDIS_URL=redis://localhost:6379/0

# --- Frontend ---
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws
```

### 27.2 Initial Setup Commands

```bash
# Clone and setup
git clone <repo>
cd usa-swing

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API keys

# Database setup
alembic upgrade head
python ../scripts/seed_symbol_registry.py
python ../scripts/seed_agent_definitions.py

# Initial model training (requires 3 years backfilled data)
python ../scripts/backfill_market_data.py --symbols SPY QQQ DIA IWM --years 3
python ../scripts/train_initial_models.py

# Start backend
uvicorn main:app --reload --port 8000

# Frontend setup (new terminal)
cd ../frontend
npm install
npm run dev

# Platform available at http://localhost:3000
```

---

*End of SPEC.md — USA Swing Platform Specification v1.0.0*  
*This document is the authoritative implementation reference. All implementation decisions must be traceable to this specification.*
