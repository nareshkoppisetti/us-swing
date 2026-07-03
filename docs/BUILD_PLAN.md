# USA Swing — Complete Developer Build Plan
**Version:** 1.0.0 | **Spec Reference:** `docs/SPEC.md` | **Status:** Implementation Ready

> This document is the authoritative step-by-step build guide for the USA Swing platform.
> Every file listed here maps directly to the project folder structure.
> Work through phases in order — each phase depends on the previous one being complete and testable.

---

## Quick Reference

| Layer | Tech | Key Files |
|-------|------|-----------|
| Frontend | Next.js 14 (CSR), Tailwind, ShadCN, Zustand, TanStack Query | `frontend/src/` |
| Backend | FastAPI, Python 3.12, SQLAlchemy 2.x, Alembic | `backend/` |
| Database (MVP) | SQLite + Parquet files + diskcache | `backend/data/` |
| ML | LightGBM, XGBoost, CatBoost, Scikit-learn, SHAP, MLflow | `backend/ml/` |
| LLM | Grok API (xAI) via HTTPX | `backend/modules/explainability/` |
| Auth | JWT (HS256), bcrypt, RBAC 4 roles | `backend/modules/auth/` |

---

## Environment Setup (Do This First — Before Any Phase)

### Step 1 — Copy and fill environment files

```
File: backend/.env.example  →  copy to  backend/.env
File: frontend/.env.local   →  already has defaults for localhost
```

Minimum keys needed to start Phase 1:
```
APP_SECRET_KEY=<generate: openssl rand -hex 32>
DATABASE_URL=sqlite:///./data/usa_swing.db
SCHEDULER_DB_URL=sqlite:///./data/scheduler.db
CACHE_DIR=./data/cache
PARQUET_DATA_DIR=./data/market_data
LOG_DIR=./logs
```

### Step 2 — Backend Python environment

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Step 3 — Frontend Node environment

```bash
cd frontend
npm install
```

### Step 4 — Verify folder structure exists

After fresh git clone, these empty dirs must exist (`.gitkeep` files ensure this):
```
backend/data/cache/
backend/data/market_data/ohlcv/
backend/data/market_data/options/
backend/data/market_data/features/
frontend/public/
ml/artifacts/
ml/feature_store/
ml/training/
```

---

## PHASE 1 — Backend Foundation
**Goal:** Running FastAPI server with database schema, auth, and health endpoint.
**Test:** `GET /health` returns 200. `POST /api/v1/auth/login` returns JWT token.
**Estimated effort:** 3–4 days

---

### 1.1 — Alembic Migration Setup

**File:** `backend/alembic/env.py`

Import all model modules so Alembic can detect tables:

```python
# Add inside env.py after existing imports:
from modules.auth.models import User, UserSession
from modules.market_data.models import Symbol
from modules.agents.models import AgentDefinition, AgentRun, AgentOutput
from modules.predictions.models import Prediction, PredictionReason, PredictionContributor
from modules.explainability.models import PredictionExplanation
from modules.news.models import NewsArticle, NewsSentiment
from modules.institutional.models import InstitutionalFlow, DarkPoolActivity, InsiderTransaction, ThirteenFHolding
from modules.options.models import OptionsSnapshot, VIXData
from modules.signals.models import TradeSignal  # renamed to avoid clash with agents.Signal enum
from modules.backtesting.models import Backtest, BacktestResult
from modules.alerts.models import Alert
from modules.monitoring.models import SystemMetrics, APIHealth, DataSourceHealth, AgentHealth, AuditLog
from modules.performance.models import PredictionPerformance
```

Then set `target_metadata = Base.metadata` (replace the existing `None`).

**Command to run after all models are written:**
```bash
cd backend
alembic revision --autogenerate -m "initial_schema"
alembic upgrade head
```

---

### 1.2 — Core: Exceptions and Middleware

**File:** `backend/core/exceptions.py`

Write these custom exception classes:
- `AppException(Exception)` — base with `status_code`, `code`, `message`
- `AuthenticationError(AppException)` — 401, code `AUTHENTICATION_FAILED`
- `AuthorizationError(AppException)` — 403, code `AUTHORIZATION_FAILED`
- `NotFoundError(AppException)` — 404, code `NOT_FOUND`
- `ValidationError(AppException)` — 422, code `VALIDATION_ERROR`
- `DataUnavailableError(AppException)` — 503, code `DATA_UNAVAILABLE`
- `RateLimitError(AppException)` — 429, code `RATE_LIMIT_EXCEEDED`

**File:** `backend/core/middleware.py`

Write two middleware functions, then call `setup_middleware(app)` from `main.py`:
1. **Request logging middleware** — log every request as JSON: method, path, status_code, duration_ms, request_id (UUID)
2. **Rate limiting middleware** — use `cache_service` to count requests per user per minute. Limits from SPEC Section 17.3:
   - `/api/v1/auth/login` → 5 req/min per IP
   - `/api/v1/symbols/search` → 30 req/min per user
   - `/api/v1/predictions/generate` → 10 req/min per user
   - `/api/v1/admin/*` → 60 req/min per user
   - All others → 120 req/min per user
3. **Global exception handler** — catch `AppException` → return standard JSON error envelope. Catch unhandled exceptions → log + return 500.

**Standard error envelope** (all endpoints must use this):
```json
{
  "success": false,
  "error": { "code": "STRING_CODE", "message": "Human message", "details": {} },
  "meta": { "request_id": "uuid", "timestamp": "ISO8601" }
}
```

**File:** `backend/dependencies.py`

Write FastAPI dependency functions:
- `get_db()` — yields SQLAlchemy session (already in `core/database.py`, re-export here)
- `get_current_user(token: str = Depends(oauth2_scheme), db = Depends(get_db))` — decode JWT, load user from DB, raise `AuthenticationError` if invalid
- `require_admin(user = Depends(get_current_user))` — raise `AuthorizationError` if role not in `[super_admin, admin]`
- `require_super_admin(user = Depends(get_current_user))` — raise `AuthorizationError` if role is not `super_admin`
- `require_analyst(user = Depends(get_current_user))` — raise `AuthorizationError` if role is `viewer`

---

### 1.3 — Auth Module

**File:** `backend/modules/auth/models.py`

Write SQLAlchemy models (see SPEC Section 10.2 for full field list):
- `User` — id (UUID), username, email, hashed_password, role (Enum: super_admin/admin/analyst/viewer), is_active, last_login, settings (JSON), created_at, updated_at
- `UserSession` — id (UUID), user_id (FK), access_token, refresh_token, device_info, ip_address, expires_at, created_at, revoked_at

**File:** `backend/modules/auth/schemas.py`

Write Pydantic v2 schemas:
- `LoginRequest` — username: str, password: str
- `TokenResponse` — access_token: str, token_type: str, user: UserOut
- `UserOut` — id, username, email, role, is_active, last_login
- `RefreshRequest` — refresh_token: str
- `UserCreate` (admin only) — username, email, password, role
- `UserUpdate` (admin only) — role, is_active

**File:** `backend/modules/auth/service.py`

Write `AuthService` class with these methods:
- `login(username, password, db) → TokenResponse` — find user by username, verify bcrypt password, create access token (15 min, HS256) + refresh token (7 days), store UserSession, update last_login
- `logout(user_id, access_token, db)` — set `revoked_at = now()` on UserSession
- `refresh(refresh_token, db) → TokenResponse` — validate refresh token is not revoked and not expired, issue new access token
- `get_me(user_id, db) → UserOut` — fetch user by ID
- `create_user(data, db) → UserOut` — admin only, hash password, insert User
- `update_user(user_id, data, db) → UserOut` — admin only, update role/is_active

**File:** `backend/modules/auth/router.py`

Register these endpoints under prefix `/api/v1/auth`:
- `POST /login` — calls `AuthService.login()`, no auth required
- `POST /logout` — requires JWT auth, calls `AuthService.logout()`
- `POST /refresh` — calls `AuthService.refresh()`
- `GET /me` — requires JWT auth, returns current user profile

---

### 1.4 — Market Data Models

**File:** `backend/modules/market_data/models.py`

Write SQLAlchemy models:
- `Symbol` — id (UUID), ticker (unique, indexed), name, asset_type (Enum: stock/etf/index/commodity/futures), exchange, sector, industry, yfinance_ticker, is_active, metadata (JSON), created_at

---

### 1.5 — Database Seed Scripts

**Command sequence (run after `alembic upgrade head`):**

```bash
cd backend
python ../scripts/seed_symbol_registry.py    # already written — run it
python ../scripts/seed_agent_definitions.py  # already written — run it
```

After seed, verify:
```bash
python -c "from core.database import SessionLocal; from modules.agents.models import AgentDefinition; db=SessionLocal(); print(db.query(AgentDefinition).count()); db.close()"
# Should print: 42
```

Also create the first Super Admin user manually:
```bash
python -c "
import sys; sys.path.insert(0, '.')
from core.database import SessionLocal
from modules.auth.service import AuthService
db = SessionLocal()
AuthService().create_user({'username': 'admin', 'email': 'admin@usaswing.com', 'password': 'CHANGE_ME', 'role': 'super_admin'}, db)
db.close()
print('Super admin created')
"
```

---

### 1.6 — Start Backend

```bash
cd backend
uvicorn main:app --reload --port 8000
```

Verify:
- `GET http://localhost:8000/health` → `{"status": "healthy"}`
- `GET http://localhost:8000/docs` → Swagger UI shows all routers
- `POST http://localhost:8000/api/v1/auth/login` with `{"username": "admin", "password": "CHANGE_ME"}` → returns JWT

---

## PHASE 2 — Symbol Search and Market Data
**Goal:** Search any US symbol, fetch OHLCV data, serve it via API.
**Test:** `GET /api/v1/symbols/search?q=AAPL` returns results. `GET /api/v1/market/ohlcv/AAPL` returns price data.
**Estimated effort:** 2–3 days

---

### 2.1 — Symbol Search Module

**File:** `backend/modules/symbol_search/symbol_registry.py`

Write `SymbolRegistry` class:
- On startup, load `backend/data/symbols/symbol_registry.json` into memory as a dict
- `search(query: str, limit: int = 10) → list[dict]` — case-insensitive substring match on ticker and name. Group results by type: stocks first, then ETFs, then indices, then commodities/futures.
- `get(ticker: str) → dict | None` — exact ticker lookup

**File:** `backend/modules/symbol_search/schemas.py`

Write Pydantic schemas:
- `SymbolSearchResult` — ticker, name, asset_type, exchange, sector
- `SymbolSearchResponse` — results: list[SymbolSearchResult], total: int

**File:** `backend/modules/symbol_search/service.py`

Write `SymbolSearchService`:
- `search(q, limit, db)` — call `SymbolRegistry.search()`, also check Symbol table for any dynamically added symbols, cache result 1 hour in diskcache with key `symbol_search:{q}`
- `get_symbol_detail(ticker, db)` — return full symbol metadata from Symbol table or registry

**File:** `backend/modules/symbol_search/router.py`

Endpoints under `/api/v1/symbols` (all require auth):
- `GET /search?q={query}&limit=10` — calls `SymbolSearchService.search()`
- `GET /{symbol}` — calls `SymbolSearchService.get_symbol_detail()`

---

### 2.2 — Market Data Collectors

All collectors live in `backend/modules/market_data/collectors/`. The base class is already structured in `collector_base.py`. Implement each one:

**File:** `backend/modules/market_data/collectors/collector_base.py`

Write abstract `CollectorBase`:
```python
class CollectorBase(ABC):
    source_name: str
    requires_api_key: bool
    daily_request_limit: int | None

    @abstractmethod
    def fetch(self, symbol: str, **kwargs) -> pd.DataFrame: pass

    def fetch_with_fallback(self, symbol: str, **kwargs) -> pd.DataFrame:
        """Try primary → secondary → raise DataUnavailableError"""
```

**File:** `backend/modules/market_data/collectors/yahoo_collector.py`

Wrap `yfinance.download()` and `yfinance.Ticker()`:
- `fetch_ohlcv(symbol, period="1y", interval="1d") → pd.DataFrame` — columns: date, open, high, low, close, volume
- `fetch_quote(symbol) → dict` — current price, change%, market cap, 52w high/low
- `fetch_options_chain(symbol) → tuple[pd.DataFrame, pd.DataFrame]` — calls and puts DataFrames
- `fetch_news(symbol, limit=20) → list[dict]` — recent news articles
- `fetch_earnings(symbol) → dict` — earnings dates and history
- No API key needed. Rate-limit protection: cache responses 5 minutes.

**File:** `backend/modules/market_data/collectors/alpha_vantage.py`

Wrap Alpha Vantage REST API (`ALPHA_VANTAGE_API_KEY`):
- `fetch_ohlcv(symbol, outputsize="full") → pd.DataFrame` — TIME_SERIES_DAILY
- Track daily request count in diskcache under key `rate_limit:alpha_vantage`. Raise `RateLimitError` if count ≥ 25.
- Used as fallback for Yahoo Finance OHLCV.

**File:** `backend/modules/market_data/collectors/stooq_collector.py`

Wrap `pandas_datareader.DataReader(symbol, 'stooq')`:
- `fetch_ohlcv(symbol, start, end) → pd.DataFrame` — no API key needed
- Secondary fallback for OHLCV after Alpha Vantage

**File:** `backend/modules/market_data/collectors/fred_collector.py`

Wrap FRED REST API (`FRED_API_KEY`):
- `fetch_series(series_id: str, limit=100) → pd.Series` — e.g. `fetch_series("DGS10")` for 10Y yield
- Key series used by agents: DGS10, DGS2, CPIAUCSL, UNRATE, M2SL, FEDFUNDS, WALCL (Fed balance sheet)
- Cache each series 24 hours: `fred:{series_id}`

**File:** `backend/modules/market_data/collectors/eia_collector.py`

Wrap EIA REST API (`EIA_API_KEY`):
- `fetch_petroleum_inventories() → dict` — weekly crude oil inventory levels (used by Agent 35)
- `fetch_natural_gas_storage() → dict` — weekly natural gas storage (used by Agent 37)
- Cache 24 hours.

**File:** `backend/modules/market_data/collectors/sec_edgar_collector.py`

Fetch SEC EDGAR data (no API key):
- `fetch_form4(symbol, days=30) → list[dict]` — insider transactions (used by Agent 19)
- `fetch_13f(symbol) → list[dict]` — institutional holdings from latest 13F filings (used by Agent 17)
- Base URL: `https://efts.sec.gov/LATEST/search-index?q={symbol}&dateRange=custom&startdt={date}&forms=4`
- Cache 6 hours.

**File:** `backend/modules/market_data/collectors/finra_ats_collector.py`

Fetch FINRA ATS weekly aggregate data (no API key):
- `fetch_ats_volume(symbol) → dict` — weekly ATS volume for symbol vs 4-week average
- Source: FINRA ATS transparency data (CSV download). Cache 24 hours.
- Always sets `is_degraded = True` (per SPEC Agent 16 note)

**File:** `backend/modules/market_data/collectors/cboe_collector.py`

Fetch CBOE public data (no API key):
- `fetch_vix_data() → dict` — VIX, VIX9D, VIX3M current values. Source: Yahoo Finance `^VIX`, `^VIX9D`, `^VXV`
- `fetch_options_chain(symbol) → pd.DataFrame` — via Yahoo Finance options (yfinance has this)
- Cache VIX 15 minutes.

**File:** `backend/modules/market_data/collectors/newsapi_collector.py`

Wrap NewsAPI REST (`NEWS_API_KEY`):
- `fetch_news(symbol, company_name, limit=20) → list[dict]` — articles from last 24 hours
- Track daily count in diskcache. Raise `RateLimitError` if ≥ 100/day.
- Each article: title, source, url, published_at, content snippet
- Cache per symbol 30 minutes: `news:{symbol}`

**File:** `backend/modules/market_data/collectors/nasdaq_data_link_collector.py`

Wrap Nasdaq Data Link / Quandl API (`NASDAQ_DATA_LINK_API_KEY`):
- `fetch_cot_data(symbol) → pd.DataFrame` — Commitment of Traders data for commodity symbols (used by Agents 35-42)
- Free tier is sufficient for MVP.

---

### 2.3 — Market Data Validators

**File:** `backend/modules/market_data/validators.py`

Write `DataValidator` class with these checks (SPEC Section 11.2):
- `validate_ohlcv(df: pd.DataFrame, symbol: str) → pd.DataFrame` — run all checks:
  - Required columns present: open, high, low, close, volume
  - No future-dated records
  - OHLC logic: high ≥ open, high ≥ close, low ≤ open, low ≤ close
  - Volume > 0 on trading days
  - Price reasonableness: current close within ±50% of previous close (flag, don't drop)
  - Add `is_complete: bool` column — False if volume is missing
- `validate_quote(quote: dict) → bool` — sanity check price fields
- Log any validation failures to `data_quality` log.

---

### 2.4 — Market Data Storage (Parquet)

**File:** `backend/modules/market_data/service.py`

Write `MarketDataService` with these methods:
- `get_ohlcv(symbol, timeframe="daily", period="1y") → pd.DataFrame`
  1. Check diskcache key `ohlcv:{symbol}:{timeframe}` (TTL 1 hour)
  2. If miss: check Parquet file at `data/market_data/ohlcv/{symbol}/daily.parquet`
  3. If Parquet missing or stale: fetch via `YahooFinanceCollector.fetch_ohlcv()` with Alpha Vantage fallback
  4. Validate with `DataValidator`
  5. Write Parquet (append new rows, deduplicate by date)
  6. Store in diskcache
  7. Return DataFrame
- `get_quote(symbol) → dict` — fetch current quote from Yahoo Finance, cache 5 min
- `get_options_chain(symbol) → tuple[pd.DataFrame, pd.DataFrame]` — calls + puts, cache 15 min
- `get_vix_data() → dict` — from CBOE collector, cache 15 min
- `update_parquet(symbol, new_df, timeframe)` — read existing Parquet, append new rows, drop duplicates, write back

**File:** `backend/modules/market_data/schemas.py`

Pydantic schemas:
- `OHLCVBar` — date, open, high, low, close, volume
- `OHLCVResponse` — symbol, timeframe, bars: list[OHLCVBar]
- `QuoteResponse` — symbol, price, change, change_pct, volume, market_cap, week52_high, week52_low

**File:** `backend/modules/market_data/router.py`

Endpoints under `/api/v1/market` (all require auth):
- `GET /ohlcv/{symbol}?timeframe=daily&period=1y` — returns OHLCV bars
- `GET /quote/{symbol}` — returns current quote
- `GET /indicators/{symbol}` — returns common technical indicators (RSI, MACD, EMA values) computed from OHLCV
- `GET /regime` — returns current market regime (calls Agent 1's last output from DB)

---

## PHASE 3 — Agent Engine Infrastructure
**Goal:** Agent registry, execution engine, and scheduler working. Running one agent end-to-end.
**Test:** `POST /api/v1/agents/1/trigger` for symbol AAPL runs Agent 1 and stores output in DB.
**Estimated effort:** 3–4 days

---

### 3.1 — Agent Registry

**File:** `backend/modules/agents/registry.py`

Write `AgentRegistry` singleton:
- `_agents: dict[int, BaseAgent]` — maps agent ID to instance
- `register(agent: BaseAgent)` — called at startup for each agent
- `get(agent_id: int) → BaseAgent` — raises `NotFoundError` if not registered
- `all() → list[BaseAgent]`
- `by_category(category: str) → list[BaseAgent]`
- At module import time, import and register all 42 agents.

Import order (all 42 must be imported here):
```python
# Direction
from modules.agents.direction.agent_01_regime_detection import RegimeDetectionAgent
from modules.agents.direction.agent_02_trend_structure import TrendStructureAgent
# ... through agent_06

# News & Macro
from modules.agents.news_macro.agent_07_news_analyst import NewsAnalystAgent
# ... through agent_14

# Institutional
from modules.agents.institutional.agent_15_sector_rotation import SectorRotationAgent
# ... through agent_20

# Strength
from modules.agents.strength.agent_21_put_call_parity import PutCallParityAgent
# ... through agent_26

# Exit & Reversal
from modules.agents.exit_reversal.agent_27_correlation_decay import CorrelationDecayAgent
# ... through agent_29

# Prediction Layer
from modules.agents.prediction_layer.agent_30_signal_aggregation import SignalAggregationAgent
# ... through agent_33

# Additional
from modules.agents.additional.agent_34_oi_structure import OIStructureAgent

# Commodity
from modules.agents.commodity.agent_35_crude_oil import CrudeOilAgent
# ... through agent_42
```

---

### 3.2 — Agent Execution Engine

**File:** `backend/modules/agents/engine.py`

Write `AgentEngine` class — this is the core orchestrator:

```
AgentEngine.run(symbol: str, horizons: list[int] = [2,5,10,20,30,60]) → dict[int, AgentOutput]
```

Execution order (SPEC Section 9.4):

Execution matches SPEC Section 12.3 exactly — 4 layers:

**Layer 1 (parallel — no dependencies):**
Agents: 1, 2, 3, 4, 7, 8, 11, 14, 19, 20, 21, 22, 26, 34, 35, 36, 37, 38, 39
Use `concurrent.futures.ThreadPoolExecutor` (agents are I/O-bound, not async).

**Layer 2 (parallel — depends on Layer 1):**
Agents: 5(←2), 6(←1,2), 9(←7), 10(←7,11), 12(←11), 13(←14), 15(←3,20), 16, 17, 18(←21,22), 23(←15,17), 24(←26), 25(←1,2), 27, 28(←14,26), 29(←3,15), 40(←35-39), 41(←7), 42(←20,40)

**Layer 3 (parallel — depends on Layer 2):**
Agent 27(←28)

**Layer 4 (sequential — Prediction Pipeline, depends on Layers 1–3):**
Agent 30(←all) → Agent 31(←30) → Agent 32(←30,31) → Agent 33(←30,31,32)

**For each agent execution:**
1. Check diskcache for recent output: `agent_output:{agent_id}:{symbol}` (TTL = agent refresh_frequency converted to seconds)
2. If cache hit and not stale: use cached output, skip re-run
3. Create `AgentRun` record in DB (status: running)
4. Call `agent.run(symbol, context)` inside try/except
5. If success: validate output, store `AgentOutput` in DB, update `AgentRun` status to success, update cache
6. If exception: log error, set `AgentRun` status to failed, create degraded `AgentOutput` with `error=str(e)`, continue (do NOT raise — this is graceful degradation)
7. Add output to context dict keyed by `agent_id`

**Graceful degradation rule:** If ≤ 10 agents fail, continue to prediction. If > 10 fail, still continue but set prediction `is_degraded = True`.

**Agent failure penalty:** Each failed agent reduces final confidence by 2 points (applied in Agent 32).

---

### 3.3 — Agent Schemas and Router

**File:** `backend/modules/agents/schemas.py`

Pydantic schemas:
- `AgentStatus` — id, name, category, tier, status (healthy/warning/failed), last_run, duration_ms, confidence, accuracy_30d, error_count_24h
- `AgentOutputResponse` — all fields from `AgentOutput` dataclass
- `AgentRunRequest` — symbol: str
- `AgentListResponse` — agents: list[AgentStatus]

**File:** `backend/modules/agents/router.py`

Endpoints under `/api/v1/agents` (all require auth):
- `GET /` — list all 42 agents with current status
- `GET /{id}` — single agent definition + status
- `GET /{id}/output/{symbol}` — latest `AgentOutput` from DB for that agent + symbol
- `GET /{id}/history?limit=20` — recent `AgentRun` records
- `POST /{id}/trigger` — manually trigger agent run for a symbol (Admin only), returns `AgentOutput`

---

### 3.4 — Background Scheduler

**File:** `backend/modules/agents/scheduler.py`

Use `APScheduler` with `AsyncIOScheduler`. Register these jobs (SPEC Section 9.5):

| Job name | Cron / Interval | Agents triggered | Note |
|----------|----------------|------------------|------|
| `collect_market_data` | Every 15 min (market hours) | N/A — just refreshes Parquet | Mon–Fri 09:30–16:15 ET |
| `run_direction_agents` | Every 15 min (market hours) | 1, 2, 3, 4, 5, 6 | For watchlist symbols |
| `run_news_macro_agents` | Every 15 min | 7, 8, 9, 10, 11, 12, 13, 14 | |
| `run_institutional_agents` | Daily 06:30 ET | 15, 16, 17, 18, 19, 20 | |
| `run_strength_agents` | Every 30 min | 21, 22, 23, 24, 25, 26 | |
| `run_commodity_agents` | Every 30 min | 35, 36, 37, 38, 39, 40, 41, 42 | |
| `run_full_pipeline` | Every 30 min (market hours) + 17:00 ET daily | All 42 agents + prediction | Major indices only: SPY, QQQ, DIA, IWM |
| `collect_economic_data` | Daily 07:00 ET | N/A — FRED data refresh | |
| `collect_news` | Every 30 min | N/A — NewsAPI fetch | |
| `run_backtests` | Weekly Sunday 02:00 | N/A — BacktestEngine | |
| `retrain_models` | Weekly Saturday midnight | N/A — ML training | |
| `cleanup_old_data` | Daily 03:00 | N/A — log rotation, cache cleanup | |

Start scheduler in `main.py` with `lifespan` event:
```python
from contextlib import asynccontextmanager
@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler.start()
    yield
    scheduler.shutdown()
app = FastAPI(lifespan=lifespan)
```

---

## PHASE 4 — Direction Agents (Agents 1–6)
**Goal:** First 6 agents fully implemented with real market data.
**Test:** Run `AgentEngine.run("SPY")` — Agents 1–6 all produce valid `AgentOutput` objects.
**Estimated effort:** 3–4 days

Each agent file must implement the `BaseAgent` interface exactly. All agents follow this pattern:

```python
from modules.agents.base_agent import BaseAgent, AgentOutput, Signal
from modules.market_data.service import MarketDataService
import time

class RegimeDetectionAgent(BaseAgent):
    agent_id = 1
    agent_name = "Regime Detection"
    category = "direction"
    refresh_frequency = "15min"
    dependencies = []
    tier = 1

    def run(self, symbol: str, context: dict) -> AgentOutput:
        start = time.time()
        try:
            # ... implementation ...
            return AgentOutput(
                agent_id=self.agent_id,
                agent_name=self.agent_name,
                signal=Signal.BULLISH,
                score=74.0,
                confidence=68.0,
                weight=0.8,
                reasoning="ADX at 34.2 confirms strong uptrend...",
                bullish_factors=["ADX > 25 (trending)", "regime_score=78"],
                bearish_factors=["Volatility ratio elevated at 1.1"],
                supporting_data={"adx": 34.2, "regime_score": 78},
                llm_ready_summary={"agent": "Regime Detection", "signal": "Bullish", "finding": "ADX at 34.2 confirms strong uptrend; regime_score=78; volatility ratio=0.9"},
                data_freshness=datetime.utcnow().isoformat(),
                execution_time_ms=int((time.time() - start) * 1000),
            )
        except Exception as e:
            return AgentOutput(
                agent_id=self.agent_id, agent_name=self.agent_name,
                signal=Signal.NEUTRAL, score=50.0, confidence=0.0, weight=0.8,
                reasoning="", bullish_factors=[], bearish_factors=[],
                supporting_data={}, llm_ready_summary={},
                data_freshness="", execution_time_ms=0,
                error=str(e)
            )
```

---

### Agent 1 — Regime Detection
**File:** `backend/modules/agents/direction/agent_01_regime_detection.py`

**Data needed:** Daily OHLCV for target symbol + SPY (Yahoo Finance)
**Calculations (SPEC Section 12.2):**
1. Compute 14-day ADX using pandas: `ADX > 25` → Trending, `ADX < 20` → Range-Bound
2. Compute 20-day and 60-day realized volatility. `vol_ratio = vol_20d / vol_60d`. If `> 1.3` → Volatile
3. Regime label: `Trending-Up`, `Trending-Down`, `Range-Bound`, `Volatile`, `Transitional`
4. Regime score: 100 = strong trend up, 50 = neutral, 0 = strong trend down
5. If Agent 6 output is in context (not first run), factor in HMM state probability
**Output fields:** regime_label, regime_score, adx_value, volatility_ratio

---

### Agent 2 — Trend Structure
**File:** `backend/modules/agents/direction/agent_02_trend_structure.py`

**Data needed:** Daily OHLCV (Yahoo Finance)
**Calculations:**
1. Compute EMA 8, 21, 50, 200 using `pandas.ewm(span=N).mean()`
2. EMA alignment score: how many of 8>21>50>200 (bullish) or 8<21<50<200 (bearish)
3. Price above/below EMA200 (bullish if above)
4. Golden Cross: EMA50 recently crossed above EMA200
5. Death Cross: EMA50 recently crossed below EMA200
6. Trend slope: linear regression over last 20 days of close prices
**Output fields:** trend_direction, ema_alignment_score, golden_cross, price_above_ema200

---

### Agent 3 — Market Breadth
**File:** `backend/modules/agents/direction/agent_03_market_breadth.py`

**Data needed:** OHLCV for 11 sector ETFs (XLK, XLF, XLE, XLV, XLI, XLY, XLP, XLRE, XLU, XLB, XLC) as S&P 500 breadth proxy
**Calculations:**
1. For each sector ETF, check if price is above 20-day, 50-day, 200-day MA
2. Breadth score = weighted average of `pct_above_20d × 0.5 + pct_above_50d × 0.3 + pct_above_200d × 0.2`
3. Advance-Decline proxy: count how many ETFs are up on the day vs down
**Output fields:** breadth_score, pct_above_20d, pct_above_50d, pct_above_200d

---

### Agent 4 — Market Momentum
**File:** `backend/modules/agents/direction/agent_04_market_momentum.py`

**Data needed:** Daily OHLCV for target symbol
**Calculations:**
1. RSI 14: `rsi = 100 - (100 / (1 + avg_gain / avg_loss))`. Bullish if RSI 40–70.
2. MACD: EMA12 − EMA26. Signal line = EMA9 of MACD. Bullish if MACD > Signal.
3. ROC 10d, 20d: `(close_today / close_Nd_ago - 1) * 100`
4. Stochastic: `%K = (close - min_14d) / (max_14d - min_14d) * 100`
5. Momentum score = composite 0–100
**Output fields:** momentum_score, rsi_14, macd_signal, roc_10, roc_20

---

### Agent 5 — Trend Following
**File:** `backend/modules/agents/direction/agent_05_trend_following.py`

**Data needed:** Daily OHLCV (Yahoo Finance). Agent 2 output from context.
**Calculations:**
1. Donchian Channel 20: upper = max(high, 20d), lower = min(low, 20d)
2. Breakout signal: close > upper channel AND volume > 1.5× 20-day avg volume
3. 52-week high/low proximity: `proximity = (close - low_52w) / (high_52w - low_52w)`
4. Keltner Channel deviation
**Output fields:** breakout_signal, channel_position, volume_confirmation

---

### Agent 6 — HMM Market State (Tier 2 — MVP Simplified)
**File:** `backend/modules/agents/direction/agent_06_hmm_market_state.py`

**MVP note:** Full HMM requires offline training. For MVP, use a rule-based state machine:
- If Agent 1 regime = Trending-Up AND Agent 2 trend_direction = Bullish → bull_probability = 0.75
- If Agent 1 regime = Trending-Down AND Agent 2 trend_direction = Bearish → bear_probability = 0.75
- Otherwise → sideways_probability = 0.60
**Production upgrade:** Replace with `hmmlearn` HMM trained on 3 years of daily returns.
**Output fields:** hmm_state, bull_probability, bear_probability, sideways_probability

---

## PHASE 5 — News & Macro Agents (Agents 7–14)
**Goal:** News sentiment, macro data, and Fed policy all feeding into agent outputs.
**Test:** `AgentEngine.run("AAPL")` — Agents 7–14 all produce outputs with news scores and macro data.
**Estimated effort:** 3 days

---

### Agent 7 — News Analyst
**File:** `backend/modules/agents/news_macro/agent_07_news_analyst.py`

**Data needed:** 50 news articles for symbol (last 24h) from `NewsAPICollector` + `YahooCollector.fetch_news()`
**Calculations:**
1. For each headline, run VADER sentiment: `SentimentIntensityAnalyzer().polarity_scores(headline)`
2. Run TextBlob polarity as secondary: `TextBlob(headline).sentiment.polarity`
3. Composite sentiment = weighted average, newer articles weighted 1.5×
4. Bullish article count: composite > 0.05. Bearish: composite < -0.05.
5. News sentiment score 0–100 (50 = neutral)
**Output fields:** news_sentiment_score, bullish_article_count, bearish_article_count, top_headline

---

### Agent 8 — Earnings Sentiment
**File:** `backend/modules/agents/news_macro/agent_08_earnings_sentiment.py`

**Data needed:** Earnings calendar from `YahooCollector.fetch_earnings(symbol)`
**Calculations:**
1. Days until next earnings: compare next_earnings_date to today
2. Last 4 quarters EPS surprise average (actual - estimate) / |estimate|
3. Post-earnings drift: average 5-day return after last 4 earnings dates
4. Earnings risk score: 0 (far away, neutral) → 100 (tomorrow, very risky)
**Output fields:** earnings_risk_score, days_to_earnings, surprise_average, post_earnings_drift

---

### Agent 9 — Event Detection
**File:** `backend/modules/agents/news_macro/agent_09_event_detection.py`

**Data needed:** Agent 7 news articles from context. FRED economic calendar (hardcode known CPI/PPI/GDP/FOMC dates or parse from Fed RSS feed).
**Calculations:**
1. Scan next 7 days for known high-impact events: CPI, PPI, GDP, FOMC, NFP (Non-Farm Payroll)
2. Event proximity score: if within 1 day → 90, within 3 days → 60, within 7 days → 30
3. Historical impact: average market move (SPY) on similar past event days
**Output fields:** event_risk_score, next_event_name, next_event_date, historical_impact

---

### Agent 10 — Macro News Impact
**File:** `backend/modules/agents/news_macro/agent_10_macro_news_impact.py`

**Data needed:** Agent 7 (news articles) and Agent 11 (macro score) from context
**Calculations:**
1. Keyword extraction from headlines — macro themes: `["inflation", "recession", "rate hike", "rate cut", "hawkish", "dovish", "default", "stimulus"]`
2. Theme impact matrix: "rate hike" in bearish regime → bearish impact. "rate cut" in bearish regime → bullish impact.
3. Composite macro news impact: -100 (very bearish) to +100 (very bullish)
**Output fields:** macro_news_impact_score, dominant_theme, theme_direction

---

### Agent 11 — Macro Analyst
**File:** `backend/modules/agents/news_macro/agent_11_macro_analyst.py`

**Data needed:** FRED series via `FREDCollector`:
- `DGS10` (10Y yield), `DGS2` (2Y yield), `CPIAUCSL` (CPI YoY), `UNRATE` (unemployment), `M2SL` (M2 money supply)
**Calculations:**
1. Yield curve slope: DGS10 − DGS2. Negative = inverted (bearish signal)
2. CPI trend: 3-month change in CPI YoY (accelerating = bearish)
3. Unemployment trend: rising = bearish, falling = bullish
4. M2 growth rate: 3-month annualized growth
5. Composite macro score 0–100 (50 = neutral)
**Output fields:** macro_score, yield_curve_slope, cpi_yoy, unemployment_rate, m2_growth

---

### Agent 12 — Federal Reserve
**File:** `backend/modules/agents/news_macro/agent_12_federal_reserve.py`

**Data needed:** FRED `FEDFUNDS` series. Agent 11 output from context.
**Calculations:**
1. Current Fed Funds Rate vs neutral rate (FRED `DFEDTARL` — target rate lower bound)
2. Rate direction: compare current to 6 months ago (hiking/cutting/holding)
3. FOMC sentiment: scan news articles for hawkish/dovish keywords in Fed-related headlines
4. Fed pivot probability: synthesize rate direction + CPI trend + unemployment trend
**Output fields:** fed_stance (hawkish/neutral/dovish), fed_funds_rate, rate_direction, fomc_sentiment_score

---

### Agent 13 — Global Liquidity (Tier 2)
**File:** `backend/modules/agents/news_macro/agent_13_global_liquidity.py`

**Data needed:** FRED `WALCL` (Fed balance sheet). Agent 14 (Dollar) from context.
**Calculations:**
1. Fed balance sheet 3-month trend: expanding (bullish) vs contracting (bearish)
2. M2 growth proxy as global liquidity indicator
3. DXY impact on liquidity (rising DXY = tightening global USD liquidity = bearish for equities)
**Output fields:** liquidity_score, balance_sheet_direction, global_m2_trend

---

### Agent 14 — Dollar Strength
**File:** `backend/modules/agents/news_macro/agent_14_dollar_strength.py`

**Data needed:** OHLCV for `UUP` (DXY ETF proxy) from Yahoo Finance
**Calculations:**
1. UUP 20-day trend: rising = DXY strengthening (bearish for stocks/commodities)
2. UUP vs 200-day EMA: above = strong dollar, below = weak dollar
3. UUP RSI 14: overbought/oversold
4. DXY signal: Bullish means DXY strong (which is generally bearish for equities — note inverted relationship for stock context)
**Output fields:** dxy_signal, dxy_trend, dxy_rsi, dxy_vs_ema200

---

## PHASE 6 — Institutional Agents (Agents 15–20)
**Goal:** Institutional flow, options, and insider data feeding agent signals.
**Estimated effort:** 3 days

---

### Agent 15 — Sector Rotation
**File:** `backend/modules/agents/institutional/agent_15_sector_rotation.py`

**Data needed:** 30-day OHLCV for all 11 sector ETFs. Agent 3 (Breadth) and Agent 20 (ETF Flows) from context.
**Calculations:**
1. Rank sectors by 30-day return
2. Determine target symbol's sector (from Symbol table or yfinance `info["sector"]`)
3. Sector rank 1 (leading) to 11 (lagging)
4. Sector momentum: is the sector's rank improving or deteriorating over 10-day vs 30-day?
**Output fields:** sector_rotation_score, sector_rank, sector_momentum, target_sector_bias

---

### Agent 16 — Dark Pool Flow (Degraded MVP)
**File:** `backend/modules/agents/institutional/agent_16_dark_pool_flow.py`

**Data needed:** FINRA ATS weekly aggregate from `FINRAATSCollector`
**Calculations:**
1. Get weekly ATS volume for symbol
2. Compare to 4-week average: above avg = accumulation signal, below = distribution
3. Always set `is_degraded = True` and `confidence = 20.0` (low confidence in MVP)
**Output fields:** dark_pool_signal, accumulation_score, distribution_score, is_degraded=True

---

### Agent 17 — 13F Accumulation
**File:** `backend/modules/agents/institutional/agent_17_13f_accumulation.py`

**Data needed:** `SECEdgarCollector.fetch_13f(symbol)`
**Calculations:**
1. Top 50 institutional holders: compare current quarter vs previous quarter
2. Net position change: total shares this quarter vs last quarter
3. Count institutions increasing vs decreasing holdings
4. Institutional accumulation score 0–100
**Note:** Data is quarterly — freeze score between filing dates (approximately every 45 days after quarter end)
**Output fields:** institutional_accumulation_score, net_position_change_pct, institutions_buying, institutions_selling

---

### Agent 18 — Whale Options Flow (Tier 2)
**File:** `backend/modules/agents/institutional/agent_18_whale_options_flow.py`

**Data needed:** Options chain from `CBOECollector`. Agent 21 (Put/Call) and Agent 22 (GEX) from context.
**Calculations:**
1. Compare each option trade size vs 30-day average single-trade size
2. Large call sweeps (OTM, large premium) = bullish whale signal
3. Large put sweeps (OTM, large premium) = bearish whale signal
4. Whale bias score: net premium ratio calls vs puts
**Output fields:** whale_flow_signal, call_premium_ratio, put_premium_ratio, whale_bias_score

---

### Agent 19 — Insider Transactions
**File:** `backend/modules/agents/institutional/agent_19_insider_transactions.py`

**Data needed:** `SECEdgarCollector.fetch_form4(symbol, days=30)`
**Calculations:**
1. Count purchases and sales in last 30 days
2. Net insider transaction value: total purchase value − total sale value
3. Insider buy rule: purchases are strongly bullish (insiders rarely buy except when confident)
4. Insider sell rule: sales are mildly bearish (may be tax/diversification — discount 50%)
**Output fields:** insider_signal, insider_buy_count, insider_sell_count, net_insider_value

---

### Agent 20 — ETF Flow Intelligence
**File:** `backend/modules/agents/institutional/agent_20_etf_flow_intelligence.py`

**Data needed:** OHLCV for symbol (if it's an ETF) and relevant sector ETF
**Calculations:**
1. For ETFs: estimate creation/redemption activity from price vs NAV spread (yfinance `info["navPrice"]`)
2. For stocks: use their sector ETF's flow as proxy (e.g. AAPL → XLK)
3. ETF flow momentum: 5-day, 10-day, 20-day rolling net flow trend
**Output fields:** etf_flow_score, inflow_trend, outflow_trend, sector_etf_flow

---

## PHASE 7 — Strength, Exit & Reversal Agents (Agents 21–29)
**Goal:** Options-based signals, VIX analysis, and cross-asset correlations.
**Estimated effort:** 3 days

---

### Agent 21 — Put/Call Parity
**File:** `backend/modules/agents/strength/agent_21_put_call_parity.py`

**Data needed:** Options chain from `YahooCollector.fetch_options_chain(symbol)`
**Calculations:**
1. Put/Call ratio by volume: `total_put_volume / total_call_volume`. < 0.7 = bullish, > 1.3 = bearish
2. Put/Call ratio by open interest
3. IV skew: avg IV of OTM puts (delta 0.25) vs OTM calls (delta 0.25)
4. 20-day rolling Put/Call average for mean reversion signal
**Output fields:** put_call_ratio, put_call_oi_ratio, iv_skew, sentiment_score

---

### Agent 22 — Gamma Exposure
**File:** `backend/modules/agents/strength/agent_22_gamma_exposure.py`

**Data needed:** Options chain with strikes, OI, IV, DTE. Current spot price.
**GEX Formula (SPEC Section 12.2):**
```python
# For each option at strike K:
# GEX_contribution = gamma × OI × 100 × spot²
# Sign: dealer is short calls (negative gamma) and long puts (positive gamma)
# Total GEX = Σ(call_GEX - put_GEX) across all strikes
```
**Use Black-Scholes gamma formula:**
```python
import numpy as np
from scipy.stats import norm

def bs_gamma(S, K, r, sigma, T):
    if T <= 0: return 0
    d1 = (np.log(S/K) + (r + 0.5*sigma**2)*T) / (sigma*np.sqrt(T))
    return norm.pdf(d1) / (S * sigma * np.sqrt(T))
```
**Output fields:** gex_value, gex_signal (positive GEX=pinning, negative=amplifying), call_wall, put_wall, zero_gamma_level

---

### Agent 23 — Factor Crowding (Tier 2)
**File:** `backend/modules/agents/strength/agent_23_factor_crowding.py`

**Data needed:** Agent 15 (Sector Rotation) and Agent 17 (13F) from context
**Calculations:**
1. Estimate factor exposure (momentum, value, quality, low-vol) from sector/institutional data
2. Crowding score: high institutional concentration in same factor = crowding risk
3. Unwind risk: crowded factor + deteriorating factor performance = high unwind risk
**Output fields:** crowding_score, dominant_factor, unwind_risk

---

### Agent 24 — Uncertainty
**File:** `backend/modules/agents/strength/agent_24_uncertainty.py`

**Data needed:** Agent 26 (VIX) and Agent 9 (Event Detection) from context. Earnings data from Agent 8.
**Calculations:**
1. VIX contribution: VIX < 15 → +0, VIX 15–20 → +15, VIX 20–30 → +30, VIX > 30 → +50
2. Event contribution: event_risk_score × 0.25
3. Earnings contribution: if earnings within 3 days → +30
4. Uncertainty score = sum of above, clipped to 0–100
**Output fields:** uncertainty_score, vix_contribution, event_contribution, earnings_contribution

---

### Agent 25 — Relative Strength
**File:** `backend/modules/agents/strength/agent_25_relative_strength.py`

**Data needed:** OHLCV for symbol + SPY + sector ETF. Agent 1 (Regime) and Agent 2 (Trend) from context.
**Calculations:**
1. RS Ratio = symbol 20d return / SPY 20d return. > 1.0 = outperforming
2. RS Ratio 60d and 120d
3. RS Momentum: is RS Ratio trending up or down?
4. Sector rank: compare symbol RS vs sector ETF peers
**Output fields:** rs_score, rs_ratio_20d, rs_ratio_60d, rs_momentum, sector_rank

---

### Agent 26 — VIX Structure
**File:** `backend/modules/agents/strength/agent_26_vix_structure.py`

**Data needed:** VIX, VIX9D (^VIX9D), VIX3M (^VXV) from Yahoo Finance
**Calculations:**
1. VIX zones: < 15 (calm), 15–20 (normal), 20–30 (elevated), > 30 (extreme fear)
2. Term structure: contango if VIX9D < VIX3M (normal). Backwardation if VIX9D > VIX3M (fear signal).
3. VIX trend: 5-day change. Rising = bearish, falling = bullish
4. Fear/Complacency score 0–100
**Output fields:** vix_level, vix_structure (contango/backwardation/flat), fear_score, volatility_regime

---

### Agent 27 — Correlation Decay (Tier 2)
**File:** `backend/modules/agents/exit_reversal/agent_27_correlation_decay.py`

**Data needed:** Agent 28 (Cross Asset Correlation) from context
**Calculations:**
1. Get rolling 20-day correlation between symbol and its sector ETF
2. Compare to 60-day baseline correlation
3. Decay signal: if current_corr − baseline_corr < -0.3 → potential regime change
**Output fields:** correlation_decay_signal, current_correlation, baseline_correlation, decay_score

---

### Agent 28 — Cross Asset Correlation
**File:** `backend/modules/agents/exit_reversal/agent_28_cross_asset_correlation.py`

**Data needed:** OHLCV for: symbol, GLD, USO (or CL=F), UUP (DXY), TLT (long bonds). Agent 14 and Agent 26 from context.
**Calculations:**
1. Compute 20-day correlation matrix: symbol vs each macro asset
2. Risk-On: symbol correlates positive with SPY/QQQ, negative with GLD/TLT
3. Risk-Off: symbol correlates negative with SPY, positive with GLD/TLT
4. Correlation breakdown: any pair deviating > 0.3 from historical norm
**Output fields:** cross_asset_regime (risk_on/risk_off/mixed), risk_on_score, correlation_matrix

---

### Agent 29 — Market Leadership
**File:** `backend/modules/agents/exit_reversal/agent_29_market_leadership.py`

**Data needed:** Agent 3 (Market Breadth) and Agent 15 (Sector Rotation) from context
**Calculations:**
1. Sector leadership rank from Agent 15 output
2. Large cap vs small cap leadership: compare SPY vs IWM 20-day returns
3. Symbol leadership within sector: compare symbol return vs sector ETF return
**Output fields:** leadership_score, sector_leadership_rank, symbol_vs_sector_rank

---

## PHASE 8 — Prediction Layer (Agents 30–33) and Prediction Engine
**Goal:** End-to-end prediction: all agents run → prediction generated for all 6 horizons.
**Test:** `POST /api/v1/predictions/generate` with `{"symbol": "AAPL"}` returns 6 predictions.
**Estimated effort:** 4 days

---

### Agent 30 — Signal Aggregation
**File:** `backend/modules/agents/prediction_layer/agent_30_signal_aggregation.py`

**Data needed:** All outputs from Agents 1–29 and 34–42 from context
**Calculations (SPEC Section 13.1):**
1. Apply tier weights: Tier 1 = 1.0×, Tier 2 = 0.7×, Tier 3 = 0.5×
2. Apply dynamic weight adjustments:
   - VIX > 25: Agent 26 weight × 1.5
   - Earnings within 3 days: Agent 8 weight × 1.5, overall confidence −15
   - FOMC within 1 day: Agent 12 weight × 2.0, overall confidence −20
   - Commodity symbol (CL, GC, NG, etc.): Agents 35–42 weight × 1.8
   - Failed agents: weight = 0
3. Compute:
   ```
   bull_score = Σ(agent_score × weight) for Bullish agents
   bear_score = Σ(agent_score × weight) for Bearish agents
   net_bull_pct = bull_score / total_weight  (0–100)
   net_bear_pct = bear_score / total_weight  (0–100)
   ```
4. Agent consensus rate: `count(agents matching final direction) / total_agents`
5. Compile top-5 bullish and top-5 bearish `llm_ready_summary` findings for LLM prompt
**Output fields:** signal_matrix, weighted_bull_score, weighted_bear_score, net_score, agent_consensus_rate, llm_findings_package

---

### Agent 31 — Ensemble Model
**File:** `backend/modules/agents/prediction_layer/agent_31_ensemble_model.py`

**Data needed:** Agent 30 signal matrix from context. Pre-trained model files from `backend/ml/artifacts/`
**MVP bootstrap:** If no trained models exist yet, use a rule-based approximation:
```python
# Rule-based fallback (use until ML models are trained)
if net_bull_pct > 55: direction = "Bullish"; prob = net_bull_pct / 100
elif net_bear_pct > 55: direction = "Bearish"; prob = net_bear_pct / 100
else: direction = "Neutral"; prob = 0.5
```
**Production:** Load `ml/artifacts/{horizon}/ensemble_model.pkl` with joblib. Run each base model, average probabilities.
**Output fields:** per horizon: direction_probability (dict: Bullish, Bearish, Neutral), ensemble_agreement_score

---

### Agent 32 — Confidence Scoring
**File:** `backend/modules/agents/prediction_layer/agent_32_confidence_scoring.py`

**Data needed:** Agent 30 and Agent 31 from context. VIX level from Agent 26. Event risk from Agent 9.
**Calculations (SPEC Section 13.3):**
```python
base_confidence = max(bullish_prob, bearish_prob) * 100
adjustments = {
    "agent_consensus_bonus": (consensus_rate - 0.5) * 20,
    "failed_agent_penalty": -2 * len(failed_agents),
    "high_vix_penalty": -max(0, (vix_level - 20) * 0.5),
    "event_proximity_penalty": -event_risk_score * 0.2,
    "historical_accuracy_bonus": (model_accuracy_30d - 0.5) * 30,
}
final_confidence = clip(base_confidence + sum(adjustments.values()), 0, 100)
```
**Output fields:** per horizon: confidence_score, confidence_components_breakdown (dict)

---

### Agent 33 — Final Prediction Engine
**File:** `backend/modules/agents/prediction_layer/agent_33_final_prediction_engine.py`

**Data needed:** Agents 30, 31, 32 from context. ATR from market data.
**Calculations (SPEC Section 13.4 and 13.5):**

**Direction:** `argmax(bullish_prob, bearish_prob, neutral_prob)` from Agent 31

**Risk Score:**
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

**Expected Move:**
```python
horizon_multipliers = {2: 0.5, 5: 1.0, 10: 1.8, 20: 2.5, 30: 3.5, 60: 5.0}
atr_20d = compute_atr(ohlcv_df, period=20)
base_expected_move = (atr_20d / current_price) * 100
expected_move_pct = base_expected_move * horizon_multipliers[horizon]
if direction == "Bearish": expected_move_pct = -abs(expected_move_pct)
```

**After completing:** fire `ExplainabilityEngine` as async background task (FastAPI `BackgroundTasks`).

**Store to DB:** Create `Prediction` record for each of the 6 horizons. Create `PredictionContributor` records (top agents by impact). Create `PredictionReason` records (bullish/bearish factors).

---

### 8.1 — Prediction Engine Service

**File:** `backend/modules/predictions/engine.py`

Write `PredictionEngine` class:
- `generate(symbol: str, db, background_tasks: BackgroundTasks) → list[Prediction]`
  1. Call `AgentEngine.run(symbol)`
  2. Agent 33 produces predictions for all 6 horizons
  3. Store all `Prediction` records to DB
  4. Add `ExplainabilityEngine.generate_explanation(prediction_id)` to `background_tasks`
  5. Broadcast via WebSocket channel `prediction_updates`
  6. Return predictions

**File:** `backend/modules/predictions/models.py`

Write SQLAlchemy models (SPEC Section 10.2):
- `Prediction` — all fields from SPEC including direction, confidence, risk_score, expected_move_pct, horizon_days, status, actual_direction (nullable), is_correct (nullable)
- `PredictionReason` — prediction_id, factor_type (bullish/bearish), factor, supporting_data, agent_id
- `PredictionContributor` — prediction_id, agent_id, agent_name, signal, score, weight, impact

**File:** `backend/modules/predictions/schemas.py`

Pydantic schemas:
- `PredictionResponse` — all prediction fields + reasons + contributors
- `GenerateRequest` — symbol: str, horizons: list[int] = [2,5,10,20,30,60]

**File:** `backend/modules/predictions/router.py`

Endpoints under `/api/v1/predictions` (all require auth):
- `GET /` — list all active predictions, filterable by symbol, horizon, direction, confidence_min
- `GET /{id}` — single prediction with full detail
- `POST /generate` — trigger full 42-agent run and prediction generation. Returns immediately with WebSocket push on completion.
- `GET /symbol/{symbol}` — all predictions for symbol
- `GET /horizon/{horizon}` — predictions by horizon (2, 5, 10, 20, 30, 60)

---

## PHASE 9 — Explainability Engine and LLM Narratives
**Goal:** Every prediction gets an LLM-generated or fallback analyst narrative.
**Test:** After generating a prediction, WebSocket receives `explanation_ready` event with narrative text.
**Estimated effort:** 2 days

---

### 9.1 — Explainability Models

**File:** `backend/modules/explainability/models.py`

Write `PredictionExplanation` SQLAlchemy model (SPEC Section 10.2):
- id (UUID), prediction_id (FK, unique), symbol, horizon_days, narrative_text, model_used, prompt_snapshot (JSON), top_bullish_factors (JSON), top_bearish_factors (JSON), generation_status (pending/complete/failed), fallback_used (bool), generated_at, created_at

---

### 9.2 — Prompt Builder

**File:** `backend/modules/explainability/prompt_builder.py`

Write `ExplanationPromptBuilder.build_prompt(context: ExplanationContext) → str`

Assemble the structured prompt exactly as in SPEC Section 14.3.1. The `ExplanationContext` dataclass needs:
- symbol, asset_name, asset_type, current_price, week52_low, week52_high
- direction, confidence, risk_score, expected_move_pct, horizon_days
- regime_label, regime_score, vix_level, vix_structure, macro_summary
- top_bullish_factors (list of llm_ready_summary dicts from agents)
- top_bearish_factors (list of llm_ready_summary dicts from agents)
- top_agents (top 3 contributors by impact)
- commodity_context (optional)
- top_headline (optional)

---

### 9.3 — LLM Client

**File:** `backend/modules/explainability/llm_client.py`

Write `async generate_explanation(prompt: str) → str` using httpx:
```python
async with httpx.AsyncClient(timeout=15.0) as client:
    response = await client.post(
        "https://api.x.ai/v1/chat/completions",
        headers={"Authorization": f"Bearer {os.environ['GROK_API_KEY']}", "Content-Type": "application/json"},
        json={"model": "grok-beta", "max_tokens": 400, "temperature": 0.3,
              "messages": [{"role": "user", "content": prompt}]}
    )
    return response.json()["choices"][0]["message"]["content"]
```

---

### 9.4 — Fallback Builder

**File:** `backend/modules/explainability/fallback_builder.py`

Write `ExplanationFallbackBuilder.build_fallback(context: ExplanationContext) → str`

Template string exactly as in SPEC Section 14.3.3. Always produce a usable narrative even without LLM.

---

### 9.5 — Explainability Engine

**File:** `backend/modules/explainability/engine.py`

Write `ExplainabilityEngine`:
- `generate_explanation(prediction_id: UUID, db)` — async method:
  1. Load `Prediction` + `PredictionContributor` records from DB
  2. Load agent outputs from DB for this symbol
  3. Build `ExplanationContext`
  4. Build prompt via `ExplanationPromptBuilder`
  5. Try: call `llm_client.generate_explanation(prompt)`, set `fallback_used = False`
  6. Except (any LLM error): call `fallback_builder.build_fallback(context)`, set `fallback_used = True`
  7. Store `PredictionExplanation` to DB
  8. Cache in diskcache: `explanation:pred_{prediction_id}` (TTL 24h)
  9. Broadcast via WebSocket channel `explanation_ready`: `{prediction_id, symbol, narrative_text, factors}`

**File:** `backend/modules/explainability/router.py`

Endpoints under `/api/v1/explanations`:
- `GET /{prediction_id}` — fetch explanation (check cache first, then DB)
- `GET /symbol/{symbol}` — latest explanation for symbol
- `POST /regenerate/{prediction_id}` — force fresh LLM call (Analyst role required)
- `GET /history/{symbol}?page=1&per_page=20` — paginated explanation history

---

## PHASE 10 — Additional and Commodity Agents (Agents 34–42)
**Goal:** Options OI structure and all commodity intelligence agents working.
**Estimated effort:** 3 days

---

### Agent 34 — Options OI Structure
**File:** `backend/modules/agents/additional/agent_34_oi_structure.py`

**Data needed:** Full options chain with all strikes and expirations from `YahooCollector.fetch_options_chain()`
**Calculations:**
1. Build OI profile: aggregate OI by strike across all expirations
2. Max Pain: strike where total option value (all holders lose most) is maximized
3. Call Wall: strike with highest total call OI
4. Put Wall: strike with highest total put OI
5. Dealer delta position: net delta exposure of dealer book
**Output fields:** oi_structure_score, max_pain, call_wall, put_wall, dealer_delta

---

### Agents 35–42 — Commodity Agents

Each commodity agent follows the same pattern. Data sources: Yahoo Finance (futures OHLCV), EIA API, Nasdaq Data Link (COT data).

**File:** `backend/modules/agents/commodity/agent_35_crude_oil.py` — CL=F / USO
- EIA weekly crude inventory (draw = bullish, build = bearish)
- Crude price vs 20/50/200 EMA
- WTI-Brent spread (via yahoo: `BZ=F` vs `CL=F`)
- OPEC keyword sentiment from NewsAPI

**File:** `backend/modules/agents/commodity/agent_36_gold_precious_metals.py` — GC=F / GLD
- Gold vs DXY inverse relationship: if DXY rising → gold bearish
- Gold vs FRED real rates (TIPS proxy: `DFII10`)
- Safe-haven demand: VIX + macro uncertainty composite

**File:** `backend/modules/agents/commodity/agent_37_natural_gas.py` — NG=F / UNG
- EIA natural gas weekly storage change vs consensus
- 5-year average seasonal pattern comparison
- Weather demand proxy (degree-days — hardcode seasonal model for MVP)

**File:** `backend/modules/agents/commodity/agent_38_silver.py` — SI=F / SLV
- Gold-Silver ratio (high ratio = silver relatively cheap)
- Industrial demand proxy via copper correlation
- Silver trend vs gold divergence

**File:** `backend/modules/agents/commodity/agent_39_copper.py` — HG=F / CPER
- Copper price trend (Dr. Copper — leading economic indicator)
- Copper vs SPY divergence
- China PMI proxy from NewsAPI keyword sentiment

**File:** `backend/modules/agents/commodity/agent_40_commodity_momentum.py`
- Composite from Agents 35–39 average scores
- Commodity cycle phase: reflation (commodities up, growth up) vs deflation

**File:** `backend/modules/agents/commodity/agent_41_commodity_sentiment.py` (Tier 2)
- News sentiment from Agent 7 filtered for commodity keywords
- Supply shock / demand shock event detection

**File:** `backend/modules/agents/commodity/agent_42_commodity_flow_positioning.py` (Tier 2)
- ETF flows for GLD, USO, SLV, UNG, CPER from Agent 20
- COT (Commitment of Traders) net positioning from Nasdaq Data Link

---

## PHASE 11 — Supporting Backend Modules
**Goal:** News, institutional, options, signals, alerts, backtesting, performance all functional.
**Estimated effort:** 4 days

---

### 11.1 — News Module

**File:** `backend/modules/news/models.py`
- `NewsArticle` — id, headline, source, url (unique), published_at, symbols (JSON), impact_score, sentiment_score, created_at
- `NewsSentiment` — id, article_id (FK), symbol, bullish_score, bearish_score, neutral_score, composite_score, analyzed_at

**File:** `backend/modules/news/sentiment.py`
- `analyze_sentiment(text: str) → dict` — run VADER and TextBlob, return composite score

**File:** `backend/modules/news/service.py`
- `NewsIntelligenceEngine` class
- `get_news(symbol, limit=20, db) → list[NewsArticle]` — fetch from DB or NewsAPICollector
- `get_economic_calendar() → list[dict]` — hardcoded upcoming economic events + FRED calendar

**File:** `backend/modules/news/router.py`
- `GET /news?symbol={symbol}&limit=20` — news feed
- `GET /news/sentiment/{symbol}` — sentiment summary
- `GET /news/economic-calendar` — upcoming events

---

### 11.2 — Institutional Module

**File:** `backend/modules/institutional/models.py`
Models: `InstitutionalFlow`, `DarkPoolActivity`, `InsiderTransaction`, `ThirteenFHolding` (all from SPEC Section 10.2)

**File:** `backend/modules/institutional/service.py`
- `get_etf_flows(symbol, db)` — query InstitutionalFlow table
- `get_insider_transactions(symbol, db)` — query InsiderTransaction table
- `get_13f_holdings(symbol, db)` — query ThirteenFHolding table
- `get_dark_pool(symbol, db)` — query DarkPoolActivity table

**File:** `backend/modules/institutional/router.py`
- `GET /institutional/etf-flows` — ETF flow summary
- `GET /institutional/insider/{symbol}` — insider transactions (last 30 days)
- `GET /institutional/13f/{symbol}` — 13F holdings
- `GET /institutional/dark-pool/{symbol}` — dark pool activity

---

### 11.3 — Options Module

**File:** `backend/modules/options/models.py`
Models: `OptionsSnapshot`, `VIXData` (from SPEC Section 10.2)

**File:** `backend/modules/options/gex_calculator.py`
- Extract GEX calculation from Agent 22 into a standalone utility (shared by options service)

**File:** `backend/modules/options/service.py`
- `OptionsIntelligenceEngine` class
- `get_options_chain(symbol, db)` — fetch from Parquet or Yahoo Finance
- `get_gex(symbol, db)` — compute GEX and return structured data
- `get_oi_structure(symbol, db)` — call wall, put wall, max pain
- `get_vix_data(db)` — current VIX snapshot

**File:** `backend/modules/options/router.py`
- `GET /options/chain/{symbol}` — full options chain
- `GET /options/gex/{symbol}` — gamma exposure data
- `GET /options/oi-structure/{symbol}` — OI structure
- `GET /options/vix` — VIX current data

---

### 11.4 — Signals Module

**File:** `backend/modules/signals/models.py`
- `TradeSignal` — id, symbol (indexed), signal_type (bullish/bearish/neutral), signal_name, strength, confidence, source_agent_id, supporting_evidence, created_at, expires_at
  > **Note:** Named `TradeSignal` (not `Signal`) to avoid runtime clash with the `Signal` enum in `modules/agents/base_agent.py`. The database table name remains `"signals"`.

**File:** `backend/modules/signals/service.py`
- `SignalEngine.generate_signals(prediction, agent_outputs, db)` — create TradeSignal records from high-confidence agent outputs (score > 70, confidence > 60)

**File:** `backend/modules/signals/router.py`
- `GET /signals?symbol={symbol}&type={type}&limit=50` — active signals
- `GET /signals/symbol/{symbol}` — signals for specific symbol

---

### 11.5 — Alerts Module

**File:** `backend/modules/alerts/models.py`
- `Alert` model from SPEC Section 10.2 (all types: prediction, regime_change, high_risk, institutional_flow, options, system, agent_failure, data_source)

**File:** `backend/modules/alerts/service.py`
- `AlertEngine` class
- `check_and_create_alerts(prediction, agent_outputs, db)` — evaluate alert thresholds:
  - Prediction confidence > 80 → high confidence alert
  - Risk score > 70 → high risk alert
  - Regime change detected (Agent 1 regime differs from last run) → regime change alert
  - > 3 agents failed → agent failure alert
- `acknowledge(alert_id, db)` — mark alert as acknowledged

**File:** `backend/modules/alerts/delivery.py`
- `DeliveryService.deliver(alert, db)` — for MVP: update `delivery_status = "delivered"` (dashboard notification via WebSocket). Email delivery: placeholder for production.

**File:** `backend/modules/alerts/router.py`
- `GET /alerts?status=active` — active alerts
- `POST /alerts` — create alert rule
- `PUT /alerts/{id}/acknowledge` — acknowledge alert

---

### 11.6 — Backtesting Module

**File:** `backend/modules/backtesting/engine.py`
- `BacktestEngine.run(symbol, horizon_days, start_date, end_date, confidence_threshold, db)`
  1. Load historical predictions from DB for symbol + horizon
  2. For each expired prediction: compare predicted direction to actual price move
  3. Compute metrics: win_rate, CAGR (annualized), Sharpe ratio, max_drawdown, monthly_returns, equity_curve

**File:** `backend/modules/backtesting/models.py`
- `Backtest` and `BacktestResult` models (from SPEC Section 10.2)

**File:** `backend/modules/backtesting/router.py`
- `POST /backtests` — run new backtest (returns immediately, runs async)
- `GET /backtests/{id}` — results when complete
- `GET /backtests/symbol/{symbol}` — history

---

### 11.7 — Performance Module

**File:** `backend/modules/performance/service.py`
- Prediction accuracy tracking: for each expired prediction, `is_correct = (actual_direction == predicted_direction)`
- `get_accuracy_metrics(horizon, symbol, rolling_days, db)` — precision, recall, F1, win rate
- `get_agent_performance_rankings(db)` — rank agents by prediction contribution accuracy
- `get_model_performance(db)` — ML model accuracy per horizon

**File:** `backend/modules/performance/router.py`
- `GET /performance/accuracy?horizon=5&rolling_days=30` — accuracy metrics
- `GET /performance/agents` — agent performance rankings
- `GET /performance/models` — ML model metrics

---

### 11.8 — Monitoring Module

**File:** `backend/modules/monitoring/models.py`
- `SystemMetric` — timestamp, cpu_pct, ram_pct, disk_pct, active_ws_connections
- `APIHealth` — endpoint, requests_1h, success_rate, avg_response_ms, p99_response_ms
- `DataSourceHealth` — source_name, status, last_update, response_time_ms, error_count, rate_limit_remaining
- `AuditLog` — user_id, action, resource_type, resource_id, old_value, new_value, ip_address, timestamp

**File:** `backend/modules/monitoring/service.py`
- `MonitoringEngine.collect_system_metrics()` — use `psutil` for CPU/RAM/disk
- `MonitoringEngine.get_agent_health_summary(db)` — count healthy/warning/failed agents
- `MonitoringEngine.write_audit_log(action, resource_type, resource_id, user_id, db)` — call this in all write endpoints

**File:** `backend/modules/monitoring/router.py`
- `GET /admin/system` — system metrics (Admin only)
- `GET /admin/agents/status` — all 42 agent health statuses
- `GET /admin/data-sources` — data source health
- `GET /admin/api-health` — endpoint metrics
- `GET /admin/logs?type=app&severity=error&page=1` — paginated log viewer

---

### 11.9 — Admin Module

**File:** `backend/modules/admin/service.py`
- `AdminService.get_system_config(db)` — read agent weights, thresholds from DB or config file
- `AdminService.update_system_config(data, db)` — Super Admin only, update agent weights in `AgentDefinition` table
- `AdminService.get_users(db)` — list all users
- Delegate to `AuthService` for user CRUD

**File:** `backend/modules/admin/router.py`
- `GET /admin/config` — system configuration (Admin only)
- `PUT /admin/config` — update configuration (Super Admin only)
- `GET /admin/users` — user list (Admin only)
- `POST /admin/users` — create user (Admin only)
- `PUT /admin/users/{id}` — update user role (Admin only)
- `DELETE /admin/users/{id}` — deactivate user (Admin only)

---

## PHASE 12 — Machine Learning Pipeline
**Goal:** Initial ML models trained and used by Agent 31.
**Test:** `backend/ml/artifacts/5d/ensemble_model.pkl` exists and loads without error.
**Estimated effort:** 3 days

---

### 12.1 — Feature Builder

**File:** `backend/ml/features/feature_builder.py`

Write `FeatureBuilder.build(symbol, agent_outputs, ohlcv_df) → pd.DataFrame`

Build all feature tiers (SPEC Section 15.1):
- **Tier 1:** returns_1d, returns_5d, returns_10d, returns_20d, realized_vol_10d, realized_vol_20d, realized_vol_60d, volume_ratio_20d, atr_20d, rsi_14, rsi_2, macd_signal, macd_histogram, price_vs_ema20, price_vs_ema50, price_vs_ema200, adx_14
- **Tier 2:** For each agent i (1–42): `agent_{i}_score`, `agent_{i}_confidence`, `agent_{i}_signal_encoded` (Bullish=1, Neutral=0, Bearish=-1)
- **Tier 3:** breadth_x_momentum (agent_3 × agent_4), vix_x_regime (agent_26 × agent_1), etf_flow_x_sector (agent_20 × agent_15), news_x_earnings (agent_7 × agent_8), commodity_momentum_x_gold (agent_40 × agent_36)
- **Tier 4:** prev_prediction_direction_encoded, rolling_model_accuracy_20d, prediction_streak, days_since_regime_change

---

### 12.2 — Feature Store

**File:** `backend/ml/features/feature_store.py`

Write `FeatureStore`:
- `save(symbol, features_df)` — write to `data/market_data/features/{symbol}/feature_matrix.parquet`
- `load(symbol) → pd.DataFrame` — read Parquet
- `append(symbol, new_row_df)` — append new feature row and save

---

### 12.3 — Initial Training Script

**File:** `scripts/train_initial_models.py`

Run this once before MVP launch. Steps (SPEC Section 15.3):
1. Load 3 years of OHLCV from Parquet (requires `backfill_market_data.py` to have run first)
2. Load historical agent outputs from DB (if insufficient, generate synthetic features from OHLCV indicators)
3. Generate labels: for each horizon H, compute `future_return`. Bullish if > +1.5%, Bearish if < -1.5%, else Neutral.
4. Walk-forward validation: 252-day training window, 21-day test window, 5 folds
5. Train base models: LightGBM, XGBoost, CatBoost, RandomForest, ExtraTrees, LogisticRegression
6. Train meta-model (LogisticRegression on OOF base model predictions)
7. Evaluate: accuracy, precision, recall, F1, ROC-AUC per fold
8. Save best ensemble to `backend/ml/artifacts/{horizon}/ensemble_model.pkl` using `joblib.dump()`
9. Register in MLflow (optional for MVP — just save pickle files)

**Run command:**
```bash
cd backend
python ../scripts/train_initial_models.py --symbols SPY QQQ DIA IWM AAPL TSLA NVDA
```

---

### 12.4 — Backfill Script

**File:** `scripts/backfill_market_data.py`

Fetch 3 years of daily OHLCV for specified symbols and write to Parquet:
```bash
python scripts/backfill_market_data.py --symbols SPY QQQ DIA IWM --years 3
```

---

## PHASE 13 — Frontend Core Pages
**Goal:** Dashboard, login, search, and prediction display all working with real backend data.
**Estimated effort:** 4 days

---

### 13.1 — Authentication Flow (Already partially done)

**Files to complete:**
- `frontend/src/hooks/useAuth.js` ✅ (updated in previous session)
- `frontend/src/lib/api.js` ✅ (updated in previous session)
- `frontend/src/app/login/page.jsx` ✅ (updated in previous session)
- `frontend/src/middleware.js` ✅ (created in previous session)

**Remaining work in login page:** Connect the form submit to the real API. Already done — verify it works end-to-end after Phase 1 backend is complete.

**Cookie flow for admins:** On login, the backend returns `user.role`. The `lib/api.js login()` function stores:
- `usa-swing-token` cookie (JWT, 15 min) — read by middleware for auth
- `usa-swing-role` cookie (string, 15 min) — read by middleware for role check

---

### 13.2 — Main Layout and Navigation

**File:** `frontend/src/components/layout/MainLayout.jsx`
- Shell: TopNav + Sidebar + content area
- Sidebar is collapsible (state from `useUIStore`)
- Mobile: overlay sidebar with backdrop
- Verify `isAdmin` from `useAuth` is passed to `Sidebar` (already wired in updated Sidebar)

**File:** `frontend/src/components/layout/TopNav.jsx`
- Logo, global search bar (always visible), user avatar/role badge, theme toggle
- Keyboard shortcut: `Ctrl+K` / `Cmd+K` opens `GlobalSearchBar`

---

### 13.3 — Global Search

**File:** `frontend/src/components/search/GlobalSearchBar.jsx`
- Full-width input bar, always visible at top of page
- On type (debounced 300ms): call `GET /api/v1/symbols/search?q={query}`
- Results grouped by type (Stocks, ETFs, Indices, Commodities)
- On select: open `SymbolDetailPanel`, call `POST /api/v1/predictions/generate`
- `Ctrl+K` focuses this input from anywhere in app

**File:** `frontend/src/components/search/SearchAutocomplete.jsx`
- Dropdown below search bar
- Group labels for each asset type
- Keyboard navigation (↑↓ arrows, Enter to select, Esc to close)

**File:** `frontend/src/components/search/SymbolDetailPanel.jsx`
- Full-page overlay (z-50) that slides in
- Sections in order (from SPEC Section 7.4):
  1. Symbol Header — ticker, name, price, change%
  2. `PriceChart` — candlestick/line toggle, timeframe selector (1D/1W/1M/3M/6M/1Y)
  3. Prediction Cards — 6 horizons using `PredictionCard` component
  4. Agent Analysis — all 42 agents grouped by category using `AgentGrid`
  5. Institutional Flows — ETF flow, insider, 13F mini-panels
  6. Options Intelligence — GEX, OI, put/call mini-panels
  7. News & Sentiment — latest 10 articles with sentiment scores
  8. Signal Explorer — active signals for this symbol
  9. Historical Predictions — last 20 predictions
  10. Backtesting Results — last backtest run
  11. AI Explanation Panel — LLM narrative (show skeleton until WebSocket `explanation_ready` fires)
- Close: Esc key or X button → back to dashboard

**File:** `frontend/src/stores/symbolStore.js`
- `selectedSymbol: string | null`
- `symbolData: object | null` — full symbol analysis package
- `setPredictions`, `setAgentOutputs`, `setExplanation` setters

**File:** `frontend/src/hooks/useSymbolSearch.js`
- `searchSymbols(q)` → calls API, returns grouped results
- `analyzeSymbol(ticker)` → triggers prediction generation, stores in symbolStore

---

### 13.4 — Dashboard Page

**File:** `frontend/src/app/dashboard/page.jsx`

Current state: Already has layout and some widgets. Complete these widget implementations:

**Widgets to implement (each in their component file under `components/dashboard/`):**

| Component File | API endpoint | Data displayed |
|----------------|-------------|----------------|
| `MarketRegimeWidget.jsx` | `GET /api/v1/market/regime` | Regime label + score badge |
| `MarketDirectionWidget.jsx` | `GET /api/v1/predictions?symbol=SPY&horizon=5` | SPY 5D direction with confidence |
| `ConfidenceScoreWidget.jsx` | Latest SPY prediction | Gauge 0–100 |
| `RiskScoreWidget.jsx` | Latest SPY prediction | Risk gauge |
| `ExpectedMoveWidget.jsx` | Latest SPY prediction | Expected move % |
| `MarketBreadthWidget.jsx` | Agent 3 latest output for SPY | Breadth score + 3 MA percentages |
| `MomentumScoreWidget.jsx` | Agent 4 latest output | RSI + MACD composite |
| `VIXStructureWidget.jsx` | `GET /api/v1/options/vix` | VIX level, term structure |
| `DXYStrengthWidget.jsx` | Agent 14 latest output | DXY trend direction |
| `SectorRotationWidget.jsx` | Agent 15 output + `SectorRotationChart` | Sector heatmap |
| `InstitutionalFlowSummary.jsx` | `GET /api/v1/institutional/etf-flows` | Flow summary |
| `ETFFlowSummary.jsx` | Same | ETF-specific flows |
| `WhaleFlowSummary.jsx` | Agent 18 output | Whale flow indicator |
| `BullishDriversWidget.jsx` | Latest SPY explanation | Top 3 bullish factors |
| `BearishDriversWidget.jsx` | Latest SPY explanation | Top 3 bearish factors |
| `AgentConsensusWidget.jsx` | Agent 30 output | Consensus rate gauge |
| `PredictionTimeline.jsx` | `GET /api/v1/predictions/symbol/SPY` | Mini timeline chart |
| `HistoricalAccuracyWidget.jsx` | `GET /api/v1/performance/accuracy` | Win rate by horizon |
| `ActiveAlertsWidget.jsx` | `GET /api/v1/alerts?status=active` | Alert count + latest |
| `MajorRisksWidget.jsx` | Agent 24 + Agent 9 outputs | Risk factor list |

**Hooks to use in dashboard:**
- `useMarketData()` — `frontend/src/hooks/useMarketData.js` → TanStack Query wrapper for market endpoints
- `usePredictions()` — `frontend/src/hooks/usePredictions.js` → predictions for SPY
- `useWebSocket()` — `frontend/src/hooks/useWebSocket.js` → subscribe to `market_data`, `prediction_updates`, `alerts` channels

---

### 13.5 — Predictions Page

**File:** `frontend/src/app/predictions/page.jsx`
- `PredictionTable` with `PredictionFilters`: filter by horizon, direction, confidence, symbol
- `HorizonSelector` tabs
- Sortable columns: confidence, risk_score, expected_move_pct, prediction_date
- Click row → opens `SymbolDetailPanel`

**Hook:** `usePredictions.js` → `GET /api/v1/predictions` with query params

---

### 13.6 — Agents Page

**File:** `frontend/src/app/agents/page.jsx`
- `AgentGrid` — 42 agents in category groups
- Each `AgentCard` shows: agent name, signal badge, score, confidence, last run time, status indicator

**Hook:** `useAgents.js` → `GET /api/v1/agents`

**File:** `frontend/src/components/agents/AgentDetailModal.jsx`
- Full breakdown for a single agent: reasoning text, bullish factors list, bearish factors list, supporting data JSON, history chart

---

## PHASE 14 — Remaining Frontend Pages
**Goal:** All pages in the spec are functional.
**Estimated effort:** 4 days

---

### Page Checklist

| Page file | Hook(s) used | Key components |
|-----------|-------------|----------------|
| `market-intelligence/page.jsx` | `useMarketData` | Regime timeline, breadth chart, sector rotation, macro indicators, correlation heatmap |
| `news/page.jsx` | `useNews` (create this hook) | News feed list, sentiment filter, economic calendar |
| `institutional-flows/page.jsx` | `useInstitutional` | ETFFlowPanel, DarkPoolPanel, InsiderTransactionPanel, ThirteenFPanel, WhaleFlowPanel |
| `options-intelligence/page.jsx` | `useOptions` | GammaExposurePanel, OIStructurePanel, PutCallPanel, VolatilityPanel, DealerPositioningPanel |
| `signals/page.jsx` | `useSignals` | Signal list, filter by type/strength, signal detail |
| `backtesting/page.jsx` | `useBacktesting` | Symbol + horizon selector, run button, EquityCurveChart, metrics cards |
| `performance/page.jsx` | `usePerformance` | AccuracyTrendChart, agent rankings table, model comparison |
| `history/page.jsx` | `useHistory` | Historical predictions table, outcome badges, accuracy filter |
| `alerts/page.jsx` | `useAlerts` | Alert list, severity badges, AlertCreator form |
| `explanations/page.jsx` | `useExplanations` | ExplanationList, ExplanationFilters, ExplanationCard |
| `settings/page.jsx` | `useAuth` | User preferences form, theme selector, default symbol |

**Missing hook to create:**
- `frontend/src/hooks/useNews.js` → `GET /api/v1/news`, `GET /api/v1/news/economic-calendar`

---

## PHASE 15 — Charts
**Goal:** All chart components rendering with real data.
**Estimated effort:** 2 days

All charts use **Recharts**. Each chart component is in `frontend/src/components/charts/`.

| Component | Chart type | Data source |
|-----------|-----------|-------------|
| `PriceChart.jsx` | Candlestick (custom) or LineChart | `GET /api/v1/market/ohlcv/{symbol}` |
| `AccuracyTrendChart.jsx` | LineChart | `GET /api/v1/performance/accuracy` |
| `GEXChart.jsx` | BarChart by strike | `GET /api/v1/options/gex/{symbol}` |
| `OIHeatmap.jsx` | Custom heatmap (recharts ScatterChart) | `GET /api/v1/options/chain/{symbol}` |
| `CorrelationHeatmap.jsx` | Custom grid (recharts or SVG) | Agent 28 output |
| `SectorRotationChart.jsx` | ScatterChart (RS vs RS Momentum) | Agent 15 output |
| `BreadthHistoryChart.jsx` | AreaChart | Agent 3 history |
| `EquityCurveChart.jsx` | AreaChart | `GET /api/v1/backtests/{id}` |
| `RegimeTimelineChart.jsx` | Gantt-style custom | Agent 1 history |

**Note on CandlestickChart:** Recharts does not have a native candlestick chart. Two options:
- **Option A (recommended — no new dependency):** Use recharts `ComposedChart` with `Bar` for the candle body and `ErrorBar` for the wick lines. This works with the recharts already installed.
- **Option B:** Install `react-financial-charts` (`npm install react-financial-charts`) for a proper OHLCV candlestick component. This package is not currently in `package.json` — add it if you choose this route.

---

## PHASE 16 — Admin Panel Pages
**Goal:** All admin sub-pages functional, connected to real backend data.
**Estimated effort:** 3 days

All admin pages use the nested layout (`app/admin/layout.jsx` ✅). No individual `AdminLayout` import needed. Access is enforced by `middleware.js` ✅.

| Page file | Component | API endpoint | Admin-specific note |
|-----------|-----------|-------------|---------------------|
| `admin/system/page.jsx` | `SystemMetricsPanel` | `GET /api/v1/admin/system` | CPU/RAM/disk real-time via WebSocket `system_health` |
| `admin/agents/page.jsx` | `AgentStatusTable` | `GET /api/v1/admin/agents/status` | Manual trigger button per agent |
| `admin/predictions/page.jsx` | Prediction monitoring table | `GET /api/v1/predictions` | Accuracy drift indicator |
| `admin/data-sources/page.jsx` | `DataSourceTable` | `GET /api/v1/admin/data-sources` | Status badge per source |
| `admin/api-health/page.jsx` | API metrics table | `GET /api/v1/admin/api-health` | P99 response time highlight |
| `admin/data-quality/page.jsx` | Data quality cards | `GET /api/v1/admin/data-sources` | Missing% and delayed% |
| `admin/alerts/page.jsx` | Alert monitoring | `GET /api/v1/alerts` | All alerts (not just active) |
| `admin/logs/page.jsx` | `LogViewer` | `GET /api/v1/admin/logs` | Severity filter + text search |
| `admin/users/page.jsx` | `UserManagementTable` | `GET /api/v1/admin/users` | Role change dropdown |
| `admin/models/page.jsx` | `ModelMonitoringTable` | `GET /api/v1/performance/models` | Drift score column |
| `admin/config/page.jsx` | `ConfigEditor` | `GET/PUT /api/v1/admin/config` | Super Admin only — weight sliders |

**Hook:** `frontend/src/hooks/useAdmin.js` → wraps all admin API calls with `require_admin` JWT

---

## PHASE 17 — WebSocket Real-Time Updates
**Goal:** Dashboard auto-updates without refresh. Explanation panel populates automatically.
**Estimated effort:** 1–2 days

---

### Backend WebSocket (already scaffolded)

**File:** `backend/core/websocket_manager.py` ✅ (already implemented)

**Channels to broadcast from (add broadcast calls in these locations):**

| Channel | Where to broadcast | Payload |
|---------|--------------------|---------|
| `market_data` | `MarketDataService.get_quote()` on cache miss | `{symbol, price, change_pct, volume}` |
| `agent_updates` | `AgentEngine` after each agent completes | `{agent_id, symbol, signal, score, timestamp}` |
| `prediction_updates` | `PredictionEngine.generate()` on completion | `{prediction_id, symbol, direction, confidence, horizon}` |
| `explanation_ready` | `ExplainabilityEngine.generate_explanation()` on completion | `{prediction_id, symbol, narrative_text, factors}` |
| `alerts` | `AlertEngine.check_and_create_alerts()` on new alert | `{alert_id, type, severity, message}` |
| `system_health` | APScheduler every 30 seconds | `{cpu, ram, disk, agent_healthy_count, agent_failed_count}` |

**WebSocket auth:** Token passed as query param `?token={jwt}`. Verify token on connect in `websocket_manager.connect()`.

---

### Frontend WebSocket

**File:** `frontend/src/lib/websocket.js` ✅ (already implemented)
**File:** `frontend/src/hooks/useWebSocket.js`

Complete this hook to:
- On mount: call `wsManager.connect(token)` where token is from cookie
- Return `subscribe(channel, callback)` function
- Handle reconnect automatically (already in `wsManager`)

**Usage in components:**
```javascript
// Example: Dashboard subscribes to live alerts
const { subscribe } = useWebSocket()
useEffect(() => {
  return subscribe('alerts', (data) => {
    useAlertStore.getState().addAlert(data)
  })
}, [])
```

---

## PHASE 18 — Ticker Bar (Live Market Prices)
**Goal:** Live price ticker scrolling across top of dashboard.
**Estimated effort:** 0.5 days

**File:** `frontend/src/components/layout/TickerBar.jsx`

Display live prices for: SPY, QQQ, DIA, IWM, VIX, GLD, CL=F (crude), BTC-USD

Fetch from `GET /api/v1/market/quote/{symbol}` on mount, refresh every 30 seconds. Or subscribe to WebSocket `market_data` channel.

Note: There are two TickerBar files:
- `frontend/src/components/layout/TickerBar.jsx` ← use this one (in MainLayout)
- `frontend/src/components/TickerBar.jsx` ← duplicate, can be deleted or kept as alias

---

## PHASE 19 — Testing
**Goal:** Core paths covered by tests. Backend unit tests for agents and services.
**Estimated effort:** 3 days

---

### Backend Tests

All tests live in `backend/tests/`.

**File:** `backend/tests/unit/test_auth.py`
- Test `AuthService.login()` with valid/invalid credentials
- Test JWT creation and decode
- Test token expiry

**File:** `backend/tests/unit/test_agents.py`
- Test each agent's `run()` method with mock market data
- Test `validate_output()` — assert score 0–100, signal enum
- Test degraded output on exception

**File:** `backend/tests/unit/test_prediction_engine.py`
- Test confidence formula with known inputs
- Test risk score calculation
- Test expected move calculation

**File:** `backend/tests/unit/test_data_validators.py`
- Test `DataValidator.validate_ohlcv()` with edge cases: missing columns, future dates, bad OHLC

**File:** `backend/tests/integration/test_api.py`
- Test `POST /api/v1/auth/login` → 200 with token
- Test protected endpoint without token → 401
- Test admin endpoint as viewer → 403
- Test `GET /api/v1/symbols/search?q=AAPL` → results
- Test `GET /api/v1/health` → 200

**File:** `backend/tests/fixtures/__init__.py`
- Write fixture functions: `mock_ohlcv_df()`, `mock_agent_output()`, `mock_prediction()`

**Run tests:**
```bash
cd backend
pytest tests/ -v
```

---

## PHASE 20 — Production Deployment
**Goal:** Backend on Railway/Render, frontend on Vercel, accessible via internet.
**Estimated effort:** 1–2 days

---

### Backend Deployment (Railway or Render)

1. Push code to GitHub
2. Connect Railway/Render to GitHub repo, set root directory to `backend/`
3. Set all environment variables in Railway/Render dashboard (copy from `.env.example`)
4. Set start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Set persistent disk volume, mount at `/app/data/` (must match PARQUET_DATA_DIR and CACHE_DIR paths)
6. First deploy: run seed commands via Railway/Render shell:
   ```bash
   alembic upgrade head
   python ../scripts/seed_symbol_registry.py
   python ../scripts/seed_agent_definitions.py
   ```

### Frontend Deployment (Vercel)

1. Connect Vercel to GitHub repo, set root directory to `frontend/`
2. Set environment variables in Vercel dashboard:
   ```
   NEXT_PUBLIC_API_URL=https://your-railway-app.up.railway.app/api/v1
   NEXT_PUBLIC_BACKEND_URL=https://your-railway-app.up.railway.app
   NEXT_PUBLIC_WS_URL=wss://your-railway-app.up.railway.app/ws
   ```
3. Deploy: `vercel deploy --prod`

### CI/CD Pipeline

**File:** `.github/workflows/deploy.yml` ✅ (already scaffolded)

Complete the workflow:
```yaml
jobs:
  test:
    - run: cd backend && pip install -r requirements.txt && pytest tests/ -v
    - run: cd frontend && npm install && npm run build

  deploy-backend:
    needs: test
    - uses: railway deploy

  deploy-frontend:
    needs: test
    - uses: vercel deploy --prod
```

---

## Development Checklist — In Order

Use this checklist to track progress:

### Environment
- [ ] `.env` created and filled (backend)
- [ ] `npm install` done (frontend)
- [ ] Python venv created and requirements installed

### Phase 1 — Backend Foundation
- [ ] `core/exceptions.py` — custom exception classes
- [ ] `core/middleware.py` — request logging + rate limiting + global exception handler
- [ ] `dependencies.py` — `get_current_user`, `require_admin`, `require_super_admin`, `require_analyst`
- [ ] `modules/auth/models.py` — User, UserSession
- [ ] `modules/market_data/models.py` — Symbol
- [ ] `alembic/env.py` — import all models
- [ ] `alembic revision --autogenerate -m "initial_schema"`
- [ ] `alembic upgrade head`
- [ ] `modules/auth/schemas.py`
- [ ] `modules/auth/service.py` — AuthService
- [ ] `modules/auth/router.py` — login, logout, refresh, me
- [ ] `scripts/seed_agent_definitions.py` — run it
- [ ] `scripts/seed_symbol_registry.py` — run it
- [ ] Create super admin user manually
- [ ] **TEST: `POST /api/v1/auth/login` returns JWT ✓**

### Phase 2 — Market Data
- [ ] `modules/market_data/collectors/collector_base.py`
- [ ] `modules/market_data/collectors/yahoo_collector.py`
- [ ] `modules/market_data/collectors/alpha_vantage.py`
- [ ] `modules/market_data/collectors/stooq_collector.py`
- [ ] `modules/market_data/collectors/fred_collector.py`
- [ ] `modules/market_data/collectors/eia_collector.py`
- [ ] `modules/market_data/collectors/sec_edgar_collector.py`
- [ ] `modules/market_data/collectors/finra_ats_collector.py`
- [ ] `modules/market_data/collectors/cboe_collector.py`
- [ ] `modules/market_data/collectors/newsapi_collector.py`
- [ ] `modules/market_data/collectors/nasdaq_data_link_collector.py`
- [ ] `modules/market_data/validators.py`
- [ ] `modules/market_data/service.py`
- [ ] `modules/market_data/schemas.py`
- [ ] `modules/market_data/router.py`
- [ ] `modules/symbol_search/symbol_registry.py`
- [ ] `modules/symbol_search/service.py`
- [ ] `modules/symbol_search/schemas.py`
- [ ] `modules/symbol_search/router.py`
- [ ] **TEST: `GET /api/v1/symbols/search?q=AAPL` returns results ✓**
- [ ] **TEST: `GET /api/v1/market/ohlcv/SPY` returns OHLCV bars ✓**

### Phase 3 — Agent Infrastructure
- [ ] `modules/agents/registry.py`
- [ ] `modules/agents/engine.py`
- [ ] `modules/agents/schemas.py`
- [ ] `modules/agents/router.py`
- [ ] `modules/agents/scheduler.py`

### Phase 4 — Direction Agents
- [ ] `agent_01_regime_detection.py`
- [ ] `agent_02_trend_structure.py`
- [ ] `agent_03_market_breadth.py`
- [ ] `agent_04_market_momentum.py`
- [ ] `agent_05_trend_following.py`
- [ ] `agent_06_hmm_market_state.py`
- [ ] **TEST: `POST /api/v1/agents/1/trigger` with AAPL returns AgentOutput ✓**

### Phase 5 — News & Macro Agents
- [ ] `agent_07_news_analyst.py`
- [ ] `agent_08_earnings_sentiment.py`
- [ ] `agent_09_event_detection.py`
- [ ] `agent_10_macro_news_impact.py`
- [ ] `agent_11_macro_analyst.py`
- [ ] `agent_12_federal_reserve.py`
- [ ] `agent_13_global_liquidity.py`
- [ ] `agent_14_dollar_strength.py`

### Phase 6 — Institutional Agents
- [ ] `agent_15_sector_rotation.py`
- [ ] `agent_16_dark_pool_flow.py`
- [ ] `agent_17_13f_accumulation.py`
- [ ] `agent_18_whale_options_flow.py`
- [ ] `agent_19_insider_transactions.py`
- [ ] `agent_20_etf_flow_intelligence.py`

### Phase 7 — Strength + Exit/Reversal Agents
- [ ] `agent_21_put_call_parity.py`
- [ ] `agent_22_gamma_exposure.py`
- [ ] `agent_23_factor_crowding.py`
- [ ] `agent_24_uncertainty.py`
- [ ] `agent_25_relative_strength.py`
- [ ] `agent_26_vix_structure.py`
- [ ] `agent_27_correlation_decay.py`
- [ ] `agent_28_cross_asset_correlation.py`
- [ ] `agent_29_market_leadership.py`

### Phase 8 — Prediction Layer
- [ ] `agent_30_signal_aggregation.py`
- [ ] `agent_31_ensemble_model.py`
- [ ] `agent_32_confidence_scoring.py`
- [ ] `agent_33_final_prediction_engine.py`
- [ ] `modules/predictions/engine.py`
- [ ] `modules/predictions/models.py`
- [ ] `modules/predictions/schemas.py`
- [ ] `modules/predictions/router.py`
- [ ] **TEST: `POST /api/v1/predictions/generate` returns 6 predictions ✓**

### Phase 9 — Explainability
- [ ] `modules/explainability/models.py`
- [ ] `modules/explainability/prompt_builder.py`
- [ ] `modules/explainability/llm_client.py`
- [ ] `modules/explainability/fallback_builder.py`
- [ ] `modules/explainability/engine.py`
- [ ] `modules/explainability/router.py`
- [ ] **TEST: WebSocket receives `explanation_ready` event after prediction ✓**

### Phase 10 — Commodity Agents
- [ ] `agent_34_oi_structure.py`
- [ ] `agent_35_crude_oil.py` through `agent_42_commodity_flow_positioning.py`

### Phase 11 — Supporting Modules
- [ ] `modules/news/` — models, sentiment, service, router
- [ ] `modules/institutional/` — models, service, router
- [ ] `modules/options/` — models, gex_calculator, service, router
- [ ] `modules/signals/` — models, service, router
- [ ] `modules/alerts/` — models, service, delivery, router
- [ ] `modules/backtesting/` — engine, models, router
- [ ] `modules/performance/` — service, router
- [ ] `modules/monitoring/` — models, service, router
- [ ] `modules/admin/` — service, router

### Phase 12 — ML Pipeline
- [ ] `scripts/backfill_market_data.py` — run it
- [ ] `ml/features/feature_builder.py`
- [ ] `ml/features/feature_store.py`
- [ ] `scripts/train_initial_models.py` — run it
- [ ] `ml/models/ensemble.py`
- [ ] `ml/models/registry.py`
- [ ] `ml/training/trainer.py`
- [ ] `ml/training/validator.py`
- [ ] **TEST: `ml/artifacts/5d/ensemble_model.pkl` loads without error ✓**

### Phase 13 — Frontend Core
- [ ] `components/layout/MainLayout.jsx` — complete
- [ ] `components/layout/TopNav.jsx` — complete
- [ ] `components/search/GlobalSearchBar.jsx`
- [ ] `components/search/SearchAutocomplete.jsx`
- [ ] `components/search/SymbolDetailPanel.jsx`
- [ ] All 20 dashboard widget components
- [ ] `app/dashboard/page.jsx` — wire all widgets
- [ ] `app/predictions/page.jsx`
- [ ] `app/agents/page.jsx`

### Phase 14 — Remaining Frontend Pages
- [ ] `app/market-intelligence/page.jsx`
- [ ] `app/news/page.jsx`
- [ ] `app/institutional-flows/page.jsx`
- [ ] `app/options-intelligence/page.jsx`
- [ ] `app/signals/page.jsx`
- [ ] `app/backtesting/page.jsx`
- [ ] `app/performance/page.jsx`
- [ ] `app/history/page.jsx`
- [ ] `app/alerts/page.jsx`
- [ ] `app/explanations/page.jsx`
- [ ] `app/settings/page.jsx`

### Phase 15 — Charts
- [ ] All 9 chart components in `components/charts/`

### Phase 16 — Admin Pages
- [ ] All 11 admin pages in `app/admin/`

### Phase 17 — WebSocket
- [ ] Add `websocket_manager.broadcast()` calls in backend services
- [ ] `hooks/useWebSocket.js` — complete
- [ ] Dashboard subscribes to live channels

### Phase 18 — Ticker Bar
- [ ] `components/layout/TickerBar.jsx` — complete

### Phase 19 — Testing
- [ ] `tests/unit/test_auth.py`
- [ ] `tests/unit/test_agents.py`
- [ ] `tests/unit/test_prediction_engine.py`
- [ ] `tests/unit/test_data_validators.py`
- [ ] `tests/integration/test_api.py`

### Phase 20 — Deployment
- [ ] Backend deployed to Railway/Render
- [ ] Frontend deployed to Vercel
- [ ] Environment variables set in both platforms
- [ ] Seed scripts run on production DB
- [ ] CI/CD pipeline configured

---

## Key Rules for Every Developer

1. **Never deviate from the BaseAgent interface.** Every agent must implement `run(symbol, context) → AgentOutput` exactly. Never add required constructor args.

2. **Never skip validation.** Every agent output must call `self.validate_output(output)` before returning. Score must be 0–100. Signal must be a `Signal` enum value.

3. **Never raise exceptions from agents.** Catch all exceptions, return a degraded `AgentOutput` with `error=str(e)`. The engine must never crash because one agent failed.

4. **Never hardcode API keys.** Read from `settings` object (which reads from `.env`). Never commit `.env` to git.

5. **Always use the cache.** Check diskcache before every external API call. Every data fetch must have a TTL set.

6. **Always use the standard API response envelope:**
   ```json
   {"success": true, "data": {...}, "meta": {"request_id": "uuid", "timestamp": "ISO8601"}}
   ```

7. **Admin endpoints must use `require_admin` dependency.** Super Admin config endpoints must use `require_super_admin`.

8. **Parquet is append-only for OHLCV.** Never truncate and rewrite. Always read → append new rows → deduplicate by date → write back.

9. **Alembic for all schema changes.** Never modify the SQLite file directly. Always `alembic revision --autogenerate` then `alembic upgrade head`.

10. **Router files must NOT define a prefix that duplicates what main.py sets.** `main.py` mounts each router at its full prefix (e.g. `prefix="/api/v1/admin"`). If the router also sets `prefix="/admin"`, endpoints become `/api/v1/admin/admin/...`. Rule: every router that is mounted with an explicit prefix in `main.py` must use `router = APIRouter(tags=["..."])` with **no prefix**. The only exception is routers mounted at a bare `prefix` in main.py — but currently all routers are mounted with full paths, so **all router files must have no prefix defined**.

10. **The frontend middleware.js is the security gate.** It runs before any page. Do not add role checks in individual pages — they will not run if the middleware already redirected.
