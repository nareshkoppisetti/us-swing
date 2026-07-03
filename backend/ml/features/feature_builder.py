"""
File path: backend/ml/features/feature_builder.py
Purpose: FeatureBuilder — constructs ML feature vectors from agent outputs.
         Called by AgentEngine (Agent 31) to prepare inputs for ensemble model.
         Per SPEC Section 15 (ML Architecture).

Feature vector structure (per SPEC):
  - 42 agent scores (0.0–100.0)
  - 42 agent confidence values
  - 42 agent weights
  - 5 category aggregate scores (Direction, News&Macro, Institutional, Strength, Commodity)
  - Market regime one-hot (5 regimes)
  - Macro context features (VIX level, DXY, yield spread)
  - Data freshness penalty (% of agents with stale data)
  
Total: ~150 features per prediction run.
"""
import logging
logger = logging.getLogger("app")


class FeatureBuilder:
    """
    Builds feature vectors from AgentOutput dicts for ML model inference.
    Also used during training to build feature matrices from historical runs.
    """

    CATEGORIES = ["direction", "news_macro", "institutional", "strength", "commodity"]
    AGENT_CATEGORIES = {
        "direction": list(range(1, 7)),
        "news_macro": list(range(7, 15)),
        "institutional": list(range(15, 21)),
        "strength": list(range(21, 27)),
        "exit_reversal": list(range(27, 30)),
        "additional": [34],
        "commodity": list(range(35, 43)),
        "prediction_layer": list(range(30, 34)),
    }

    def build(self, agent_outputs: dict, symbol: str = None) -> dict:
        """
        Build feature vector from agent outputs dict.
        
        Args:
            agent_outputs: Dict {agent_id: AgentOutput}
            symbol: Optional ticker for symbol-specific features
        
        Returns:
            Feature dict with named keys (for LightGBM/XGBoost native API).
        
        TODO: Implement following steps:
          1. Extract score, confidence, weight per agent (agents 1-42)
          2. Compute category aggregates (weighted average per group)
          3. Extract macro features from specific agents (Agent 11, 14, 26)
          4. Compute data freshness penalty
          5. Return flat dict of feature_name -> float
        """
        raise NotImplementedError

    def build_matrix(self, historical_runs: list) -> tuple:
        """
        Build training feature matrix X and label vector y from historical data.
        
        Args:
            historical_runs: List of {agent_outputs, actual_direction}
        
        Returns:
            (X: list[dict], y: list[int])  — 1=Bullish, 0=Bearish, skip Neutral
        
        TODO: Implement for model training pipeline
        """
        raise NotImplementedError

    def get_feature_names(self) -> list[str]:
        """Return ordered list of feature names matching build() output keys."""
        names = []
        for i in range(1, 43):
            names += [f"agent_{i:02d}_score", f"agent_{i:02d}_confidence", f"agent_{i:02d}_weight"]
        for cat in self.CATEGORIES:
            names += [f"cat_{cat}_score", f"cat_{cat}_confidence"]
        names += ["vix_level", "dxy_trend", "yield_spread", "data_freshness_penalty",
                  "regime_trending_up", "regime_trending_down", "regime_range_bound",
                  "regime_volatile", "regime_transitional"]
        return names
