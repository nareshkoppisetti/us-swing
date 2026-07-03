# USA Swing — REST API Reference

**File path:** `docs/API.md`  
**Purpose:** Complete REST API endpoint reference for the USA Swing platform.  
**Base URL:** `http://localhost:8000/api/v1` (development)  
**Auth:** Bearer JWT in Authorization header for all endpoints except `/auth/login`.

---

## Authentication

### POST /auth/login
Authenticate and receive JWT tokens.

**Request:**
```json
{ "username": "analyst1", "password": "secret" }
```
**Response:**
```json
{ "access_token": "...", "refresh_token": "...", "token_type": "bearer", "expires_in": 900 }
```

### POST /auth/logout
Revoke refresh token session.

### POST /auth/refresh
Exchange refresh token for new access token.

### GET /auth/me
Return current authenticated user profile.

---

## Predictions

### GET /predictions
List predictions with optional filters.

**Query params:** `symbol`, `horizon`, `direction`, `status`, `page`, `page_size`

### GET /predictions/{id}
Get single prediction with full detail.

### GET /predictions/{id}/contributors
Get agent contribution breakdown for a prediction.

### POST /predictions/generate
Trigger 42-agent pipeline + prediction generation for a symbol.

**Query params:** `symbol` (required)

---

## Market Data

### GET /market/ohlcv
Fetch OHLCV bars.

**Query params:** `symbol`, `timeframe` (daily|weekly|monthly), `days`

### GET /market/indicators
Get computed technical indicators (SMA, EMA, RSI, MACD, ATR, Bollinger Bands).

**Query params:** `symbol`

---

## Agents

### GET /agents
List all 42 agent definitions + latest health status.

### GET /agents/{id}
Get agent definition and current status by ID (1–42).

### GET /agents/{id}/output
Get latest AgentOutput for a specific agent and symbol.

**Query params:** `symbol`

### POST /agents/{id}/trigger
Manually trigger an agent run (admin only).

---

## Explanations

### GET /explanations
List explanations. **Query params:** `symbol`, `horizon`, `direction`

### GET /explanations/{prediction_id}
Get explanation for a specific prediction.

### POST /explanations/regenerate/{prediction_id}
Regenerate LLM narrative (analyst/admin only).

---

## News

### GET /news
List recent articles. **Query params:** `symbol`, `hours`

### GET /news/sentiment
Aggregated sentiment for a symbol. **Query params:** `symbol`, `hours`

### GET /news/impact
High-impact news sorted by impact_score.

---

## Institutional Flows

### GET /institutional/dark-pool
ATS dark pool aggregate data. **Query params:** `symbol`, `weeks`

### GET /institutional/13f
13F institutional holdings. **Query params:** `symbol`, `quarters`

### GET /institutional/insider
Insider transactions (Form 4). **Query params:** `symbol`, `days`

### GET /institutional/etf-flows
ETF inflow/outflow summary. **Query params:** `symbol`

---

## Options Intelligence

### GET /options/chain
Full options chain. **Query params:** `symbol`

### GET /options/put-call-ratio
Put/call OI ratio. **Query params:** `symbol`

### GET /options/gamma-exposure
Dealer GEX by strike and gamma flip. **Query params:** `symbol`

### GET /options/max-pain
Max pain strike price. **Query params:** `symbol`, `expiry`

### GET /options/vix-structure
VIX term structure (VIX9D, spot, 3M, 6M).

---

## Signals

### GET /signals
List signals. **Query params:** `symbol`, `active_only`

### GET /signals/{id}
Single signal detail.

### POST /signals/{id}/invalidate
Manually invalidate a signal (admin). **Query params:** `reason`

---

## Backtesting

### POST /backtesting/run
Trigger walk-forward backtest. **Body:** BacktestRequest

### GET /backtesting
List all backtest runs. **Query params:** `symbol`

### GET /backtesting/{id}
Get backtest by ID.

### GET /backtesting/{id}/results
Get backtest performance metrics.

---

## Performance

### GET /performance/accuracy
Accuracy summary. **Query params:** `symbol`, `horizon`, `days`

### GET /performance/calibration
Confidence calibration report by bucket.

### GET /performance/history
Resolved prediction history. **Query params:** `symbol`, `limit`

### POST /performance/resolve
Trigger prediction resolution for expired predictions (admin).

---

## Alerts

### GET /alerts
List current user's alerts.

### POST /alerts
Create a new alert. **Body:** AlertCreate

### DELETE /alerts/{id}
Delete an alert.

### PATCH /alerts/{id}
Update alert settings.

---

## Symbols

### GET /symbols/search
Fuzzy search. **Query params:** `q`, `limit`

### GET /symbols
List all symbols. **Query params:** `symbol_type`, `page`, `page_size`

### GET /symbols/{ticker}
Get symbol details.

---

## Monitoring (Admin)

### GET /monitoring/health
Full system health dashboard.

### GET /monitoring/agents
All 42 agent health statuses.

### GET /monitoring/data-sources
Data source circuit breaker states.

### GET /monitoring/api-keys
External API request counts vs daily limits.

### GET /monitoring/metrics
Latest system resource metrics.

---

## Admin

### GET/POST /admin/users
List / create users.

### PATCH/DELETE /admin/users/{id}
Update / deactivate a user.

### GET /admin/scheduler/jobs
List scheduled jobs with next run times.

### POST /admin/scheduler/{job_id}/trigger
Manually trigger a job.

### GET/PATCH /admin/settings
Get / update platform settings.

---

## WebSocket

### WS /ws
Real-time event stream. Events:
- `new_prediction` — new prediction generated for a symbol
- `explanation_ready` — LLM explanation generated
- `agent_status_update` — agent health status changed
- `alert_triggered` — user alert condition met
- `system_health_update` — system metric threshold breached
