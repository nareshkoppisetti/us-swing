# USA Swing — Quickstart

This package includes your real SQLite database (`backend/data/usa_swing.db`)
with two accounts already seeded, and 7 backend modules that were previously
stubs are now fully implemented and live-tested.

## 1. Backend

```bash
cd usa-swing/backend
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt   # bcrypt is pinned to 4.0.1 — do not upgrade it,
                                   # passlib 1.7.4 breaks on bcrypt>=4.1
```

Your `.env` is already included with a valid `APP_SECRET_KEY` and correct
key names. Fill in real API keys (Alpha Vantage, FRED, EIA, NewsAPI, Grok)
for live data — the app runs and degrades gracefully without them.

### Start the API

```bash
uvicorn main:app --reload --port 8000
curl http://localhost:8000/health
```

## 2. Frontend

In a second terminal:

```bash
cd usa-swing/frontend
npm install
npm run dev
```

Open http://localhost:3000/login and sign in with either account:

| Username | Password | Role |
|---|---|---|
| `admin` | `Admin123!` | admin |
| `john` | `John123!` | user |

Change these passwords after your first login. To add more accounts:

```bash
cd usa-swing/backend && source venv/bin/activate
python scripts/seed_admin_user.py --username NAME --email EMAIL --password PASSWORD --role admin|user
python scripts/seed_admin_user.py --list   # see all existing accounts
```

## What was fixed vs. the original zip

1. **Empty `users` table** — no account existed to log in with. Added
   `backend/scripts/seed_admin_user.py`; two accounts are pre-seeded in the
   included database (see table above).
2. **`bcrypt` 5.x / `passlib` 1.7.4 incompatibility** — password hashing
   threw `ValueError: password cannot be longer than 72 bytes`. Pinned
   `bcrypt==4.0.1` in `requirements.txt`.
3. **Simplified to two roles: `admin` and `user`**, enforced identically on
   the frontend (hidden tabs + middleware redirect to `/403`) and backend
   (`require_admin` dependency on every admin-only route — verified a
   `user` account gets a real `403` even calling the API directly).
4. **`.env` key name mismatch** — had `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` but
   `config.py` only reads `ACCESS_TOKEN_EXPIRE_MINUTES`, silently ignored.
   Fixed in the included `.env`.
5. **Frontend login response-shape bug** — `/auth/login` returns its payload
   flat, but `lib/api.js`'s `login()` expected a `{success, data, meta}`
   wrapper, throwing "invalid credentials" even with the right password.
6. **Broken Stooq data fallback** — `pandas_datareader`'s built-in Stooq
   source was removed from the installed library version, so this fallback
   always failed with `NotImplementedError`. Rewrote the collector to hit
   Stooq's public CSV export endpoint directly.
7. **Agent output persistence was silently failing on every single run**
   (`AgentOutput` model had no `agent_name` column, and a required
   `agent_run_id` was never set). This broke History, Backtesting, and
   Performance entirely. Fixed and confirmed with a real 42-agent run:
   42/42 outputs persisted, readable via `/predictions/{symbol}` and
   `/signals/{symbol}`.
8. **Built out 7 backend modules that were 100% stubs** (every endpoint
   returned `501 NOT_IMPLEMENTED`): **Admin, Monitoring, Options,
   Institutional, Alerts, Backtesting, Performance**. All have real logic
   now, verified live via curl, and — where the sandbox's network
   restrictions blocked live external calls (Yahoo/SEC/Stooq) — verified
   with hand-computed synthetic tests instead (Black-Scholes GEX, max pain,
   Sharpe ratio, max drawdown, alert-matching logic all confirmed correct).
9. **Routing prefix mismatches vs. your SPEC.md** — Monitoring was mounted
   under `/admin` instead of `/monitoring`; Backtesting was mounted under
   `/backtests` instead of `/backtesting`. Fixed on both backend and
   frontend.

### Known limitations (not fixed — flagged, not hidden)

- **No per-agent accuracy tracking.** Scoring each of the 42 agents
  individually against real outcomes wasn't built (would be a meaningful
  next phase). The Performance page's agent table shows real *operational*
  health (run status, error counts) instead of fabricated accuracy numbers.
- **Email alert delivery** is implemented but no-ops with a logged message
  until you add `SMTP_HOST` / `SMTP_PORT` / `SMTP_USER` / `SMTP_PASSWORD` /
  `SMTP_FROM_ADDRESS` to `.env` (those keys don't exist in `config.py` yet).
- **Automatic alert triggering** (wiring `evaluate_alerts()` into the
  scheduler/market-data collector so alerts fire on their own) isn't wired
  in yet. The Alerts tab itself — create/list/update/delete — is fully
  functional; you'd trigger evaluation manually or as a future scheduled job.
- **Backtesting depends on prediction history accumulating.** It replays
  your system's own past Agent 33 outputs against real price outcomes,
  rather than reconstructing what all 42 agents *would have* said on
  arbitrary historical dates (that would require re-running the full
  pipeline against point-in-time data for every day in range — out of
  scope here). Run `/agents/run` for a symbol repeatedly over time to build
  up backtestable history for it.
