"""Insert all 42 agent definitions into SQLite."""
import sys
sys.path.insert(0, "../backend")

from core.database import SessionLocal
from modules.agents.models import AgentDefinition

AGENTS = [
    (1,  "Regime Detection",             "direction",        1, "15min",  []),
    (2,  "Trend Structure",              "direction",        1, "15min",  []),
    (3,  "Market Breadth",               "direction",        1, "15min",  []),
    (4,  "Market Momentum",              "direction",        1, "15min",  []),
    (5,  "Trend Following",              "direction",        1, "15min",  [2]),
    (6,  "HMM Market State",             "direction",        2, "hourly", [1, 2]),
    (7,  "News Analyst",                 "news_macro",       1, "30min",  []),
    (8,  "Earnings Sentiment",           "news_macro",       1, "daily",  []),
    (9,  "Event Detection",              "news_macro",       1, "30min",  [7]),
    (10, "Macro News Impact",            "news_macro",       1, "30min",  [7, 11]),
    (11, "Macro Analyst",                "news_macro",       1, "daily",  []),
    (12, "Federal Reserve",              "news_macro",       1, "daily",  [11]),
    (13, "Global Liquidity",             "news_macro",       2, "daily",  [14]),
    (14, "Dollar Strength",              "news_macro",       1, "hourly", []),
    (15, "Sector Rotation",              "institutional",    1, "daily",  [3, 20]),
    (16, "Dark Pool Flow",               "institutional",    2, "daily",  []),
    (17, "13F Accumulation",             "institutional",    1, "weekly", []),
    (18, "Whale Options Flow",           "institutional",    2, "daily",  [21, 22]),
    (19, "Insider Transactions",         "institutional",    1, "daily",  []),
    (20, "ETF Flow Intelligence",        "institutional",    1, "daily",  []),
    (21, "Put Call Parity",              "strength",         1, "hourly", []),
    (22, "Gamma Exposure",               "strength",         1, "hourly", []),
    (23, "Factor Crowding",              "strength",         2, "daily",  [15, 17]),
    (24, "Uncertainty",                  "strength",         1, "hourly", [26]),
    (25, "Relative Strength",            "strength",         1, "daily",  [1, 2]),
    (26, "VIX Structure",                "strength",         1, "hourly", []),
    (27, "Correlation Decay",            "exit_reversal",    2, "daily",  [28]),
    (28, "Cross Asset Correlation",      "exit_reversal",    1, "daily",  [14, 26]),
    (29, "Market Leadership",            "exit_reversal",    1, "daily",  [3, 15]),
    (30, "Signal Aggregation",           "prediction_layer", 1, "per_run",[]),
    (31, "Ensemble Model",               "prediction_layer", 1, "per_run",[30]),
    (32, "Confidence Scoring",           "prediction_layer", 1, "per_run",[30, 31]),
    (33, "Final Prediction Engine",      "prediction_layer", 1, "per_run",[30, 31, 32]),
    (34, "Options OI Structure",         "additional",       1, "hourly", []),
    (35, "Crude Oil Intelligence",       "commodity",        1, "daily",  []),
    (36, "Gold & Precious Metals",       "commodity",        1, "daily",  []),
    (37, "Natural Gas Intelligence",     "commodity",        1, "daily",  []),
    (38, "Silver Intelligence",          "commodity",        1, "daily",  []),
    (39, "Copper Intelligence",          "commodity",        1, "daily",  []),
    (40, "Commodity Momentum",           "commodity",        1, "daily",  [35, 36, 37, 38, 39]),
    (41, "Commodity Sentiment",          "commodity",        2, "daily",  [7]),
    (42, "Commodity Flow & Positioning", "commodity",        2, "daily",  [20, 40]),
]

DEFAULT_WEIGHTS = {
    "direction": 0.8, "news_macro": 0.7, "institutional": 0.75,
    "strength": 0.7, "exit_reversal": 0.6, "prediction_layer": 1.0,
    "additional": 0.65, "commodity": 0.75,
}

def seed():
    db = SessionLocal()
    try:
        for (id_, name, cat, tier, freq, deps) in AGENTS:
            existing = db.query(AgentDefinition).filter_by(id=id_).first()
            if not existing:
                db.add(AgentDefinition(
                    id=id_, name=name, category=cat, tier=tier,
                    refresh_frequency=freq, dependencies=deps,
                    default_weight=DEFAULT_WEIGHTS.get(cat, 0.7),
                    is_active=True,
                    description=f"Agent {id_}: {name}",
                ))
        db.commit()
        print(f"Seeded {len(AGENTS)} agent definitions.")
    finally:
        db.close()

if __name__ == "__main__":
    seed()
