"""
File path: backend/scripts/seed_agent_definitions.py
Purpose: Seed the agent_definitions table with all 42 agent metadata records.
         Run once after initial database migration.

Usage:
    cd backend && python scripts/seed_agent_definitions.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from core.database import SessionLocal, init_db
from modules.agents.models import AgentDefinition

# All 42 agents — (id, name, category, tier, refresh_frequency, dependencies, description)
AGENTS = [
    (1,  "Regime Detection",               "Direction",        1, "15min",  [],                    "Classifies market regime: Trending-Up, Trending-Down, Range-Bound, Volatile, Transitional"),
    (2,  "Trend Structure",                "Direction",        1, "15min",  [],                    "Analyzes price trend via higher highs/lows and MA alignment"),
    (3,  "Market Breadth",                 "Direction",        1, "15min",  [],                    "Computes % stocks above SMA50/200, advance/decline ratio"),
    (4,  "Market Momentum",                "Direction",        1, "15min",  [],                    "Measures RSI, MACD, rate of change momentum"),
    (5,  "Trend Following",                "Direction",        1, "15min",  [2],                   "EMA crossovers, Donchian channel breakouts"),
    (6,  "HMM Market State",               "Direction",        2, "hourly", [1, 2],                "Hidden Markov Model market state classification"),
    (7,  "News Analyst",                   "News & Macro",     1, "30min",  [],                    "Aggregates news headline sentiment for the symbol"),
    (8,  "Earnings Sentiment",             "News & Macro",     1, "daily",  [],                    "Analyzes earnings reports, guidance, analyst estimates"),
    (9,  "Event Detection",                "News & Macro",     1, "30min",  [7],                   "Detects high-impact events: Fed meetings, CPI, earnings"),
    (10, "Macro News Impact",              "News & Macro",     1, "30min",  [7, 11],               "Assesses macro news impact on the symbol"),
    (11, "Macro Analyst",                  "News & Macro",     1, "daily",  [],                    "Analyzes GDP, unemployment, inflation, yield curve"),
    (12, "Federal Reserve",                "News & Macro",     1, "daily",  [11],                  "Analyzes FOMC policy stance and rate decisions"),
    (13, "Global Liquidity",               "News & Macro",     2, "daily",  [14],                  "Assesses M2, central bank balance sheets"),
    (14, "Dollar Strength",                "News & Macro",     1, "hourly", [],                    "Tracks DXY trend and equity/commodity impact"),
    (15, "Sector Rotation",                "Institutional",    1, "daily",  [3, 20],               "Detects capital rotation across S&P 500 sectors"),
    (16, "Dark Pool Flow",                 "Institutional",    2, "daily",  [],                    "Analyzes ATS dark pool aggregate volume data"),
    (17, "13F Accumulation",               "Institutional",    1, "weekly", [],                    "Analyzes SEC 13F institutional buying/selling trends"),
    (18, "Whale Options Flow",             "Institutional",    2, "daily",  [21, 22],              "Detects unusually large options trades"),
    (19, "Insider Transactions",           "Institutional",    1, "daily",  [],                    "Monitors SEC Form 4 insider purchases and sales"),
    (20, "ETF Flow Intelligence",          "Institutional",    1, "daily",  [],                    "Tracks ETF inflow/outflow for symbol and sector ETFs"),
    (21, "Put Call Parity",                "Strength",         1, "hourly", [],                    "Analyzes put/call ratio for directional bias"),
    (22, "Gamma Exposure",                 "Strength",         1, "hourly", [],                    "Computes dealer GEX and gamma flip level"),
    (23, "Factor Crowding",                "Strength",         2, "daily",  [15, 17],              "Detects momentum/value factor crowding risks"),
    (24, "Uncertainty",                    "Strength",         1, "hourly", [26],                  "Measures VIX level, term structure, IV/RV spread"),
    (25, "Relative Strength",              "Strength",         1, "daily",  [1, 2],                "Computes RS vs SPY, sector ETF, and peer group"),
    (26, "VIX Structure",                  "Strength",         1, "hourly", [],                    "Analyzes VIX term structure: contango vs backwardation"),
    (27, "Correlation Decay",              "Exit & Reversal",  2, "daily",  [28],                  "Detects breakdown in historical correlations"),
    (28, "Cross Asset Correlation",        "Exit & Reversal",  1, "daily",  [14, 26],              "Analyzes equity/bond/gold/DXY correlations"),
    (29, "Market Leadership",              "Exit & Reversal",  1, "daily",  [3, 15],               "Assesses breadth quality and sector concentration"),
    (30, "Signal Aggregation",             "Prediction Layer", 1, "per_run",[],                    "Aggregates all agent signals into weighted composite score"),
    (31, "Ensemble Model",                 "Prediction Layer", 1, "per_run",[30],                  "Runs ML ensemble (LightGBM+XGBoost+RF+LR)"),
    (32, "Confidence Scoring",             "Prediction Layer", 1, "per_run",[30, 31],              "Computes final confidence: consensus%, model agreement"),
    (33, "Final Prediction Engine",        "Prediction Layer", 1, "per_run",[30, 31, 32],         "Compiles final predictions for all 6 horizons"),
    (34, "Options OI Structure",           "Additional",       1, "hourly", [],                    "Analyzes OI: call wall, put wall, max pain"),
    (35, "Crude Oil Intelligence",         "Commodity",        1, "daily",  [],                    "EIA inventory, supply/demand, CL price trend"),
    (36, "Gold & Precious Metals",         "Commodity",        1, "daily",  [],                    "Real yields, DXY, safe-haven demand, COT positioning"),
    (37, "Natural Gas Intelligence",       "Commodity",        1, "daily",  [],                    "EIA storage, weather demand, seasonal patterns"),
    (38, "Silver Intelligence",            "Commodity",        1, "daily",  [],                    "Industrial/precious dual demand, gold/silver ratio"),
    (39, "Copper Intelligence",            "Commodity",        1, "daily",  [],                    "LME inventories, China demand proxy, Dr. Copper signal"),
    (40, "Commodity Momentum",             "Commodity",        1, "daily",  [35,36,37,38,39],      "Aggregate momentum across all tracked commodities"),
    (41, "Commodity Sentiment",            "Commodity",        2, "daily",  [7],                   "Commodity news sentiment: geopolitical supply risks"),
    (42, "Commodity Flow & Positioning",   "Commodity",        2, "daily",  [20, 40],              "COT report net positions, managed money flows"),
]


def seed():
    init_db()
    db = SessionLocal()
    try:
        added = 0
        for row in AGENTS:
            aid, name, cat, tier, freq, deps, desc = row
            existing = db.get(AgentDefinition, aid)
            if existing:
                # Update in case description changed
                existing.name = name
                existing.category = cat
                existing.tier = tier
                existing.refresh_frequency = freq
                existing.dependencies = deps
                existing.description = desc
            else:
                db.add(AgentDefinition(
                    id=aid, name=name, category=cat, tier=tier,
                    refresh_frequency=freq, dependencies=deps, description=desc,
                ))
                added += 1
        db.commit()
        print(f"✓ Agent definitions seeded: {added} added, {42 - added} updated")
    except Exception as e:
        db.rollback()
        print(f"✗ Seed failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
