# USA Swing — Institutional-Grade Market Intelligence & Swing Trading Prediction Platform

## Overview
USA Swing is a modular, institutional-quality market intelligence platform covering all US equities, ETFs, indices, and commodities. It combines 42 specialized AI agents with ML ensemble models and LLM-generated analyst narratives to produce explainable, auditable swing trading predictions.

## Quick Start

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env       # Fill in your API keys
alembic upgrade head
python ../scripts/seed_symbol_registry.py
python ../scripts/seed_agent_definitions.py
uvicorn main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

Platform available at http://localhost:3000

## Architecture
- **Frontend:** Next.js (CSR), Tailwind CSS, ShadCN UI, Zustand, TanStack Query
- **Backend:** FastAPI (Python 3.12), SQLAlchemy 2.x, APScheduler, Pydantic v2
- **Storage:** SQLite (MVP) → PostgreSQL (Production), Parquet files, diskcache
- **ML:** LightGBM, XGBoost, CatBoost, scikit-learn ensemble, MLflow, SHAP
- **LLM:** xAI Grok API for analyst narrative generation

## 42 Agents
| Category | Agents |
|---|---|
| Direction | 1–6 (Regime, Trend, Breadth, Momentum, Trend Following, HMM) |
| News & Macro | 7–14 (News, Earnings, Events, Macro Impact, Macro Analyst, Fed, Liquidity, DXY) |
| Institutional | 15–20 (Sector Rotation, Dark Pool, 13F, Whale Options, Insider, ETF Flows) |
| Strength | 21–26 (Put/Call, GEX, Factor Crowding, Uncertainty, Relative Strength, VIX) |
| Exit & Reversal | 27–29 (Correlation Decay, Cross-Asset Correlation, Market Leadership) |
| Prediction Layer | 30–33 (Signal Aggregation, Ensemble Model, Confidence Scoring, Final Prediction) |
| Additional | 34 (Options OI Structure) |
| Commodity | 35–42 (Crude Oil, Gold, Natural Gas, Silver, Copper, Momentum, Sentiment, Flow) |

## Prediction Horizons
2D • 5D • 10D • 20D • 30D • 60D

## Docs
- [Full Spec](docs/SPEC.md)
- [API Reference](docs/API.md)
- [Agent Developer Guide](docs/AGENT_GUIDE.md)
