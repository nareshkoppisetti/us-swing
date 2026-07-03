"""
File path: backend/modules/explainability/engine.py
Purpose: ExplainabilityEngine — compiles agent attributions and generates LLM narratives.
         Called async after PredictionEngine completes (per SPEC Section 14).

Responsibilities:
  1. Collect top bullish/bearish factors from all agent outputs
  2. Build attribution table (agent contributions with weights)
  3. Call LLM (Grok) for analyst narrative via llm_client.py + prompt_builder.py
  4. On LLM failure: use fallback_builder.py for template narrative
  5. Persist PredictionExplanation to DB
  6. Broadcast "explanation_ready" event via WebSocket
"""
import logging
from sqlalchemy.orm import Session
logger = logging.getLogger("app")

class ExplainabilityEngine:
    def __init__(self, db: Session, cache=None):
        self.db = db
        self.cache = cache

    async def generate(self, prediction_id: str, symbol: str, horizon_days: int, agent_outputs: dict) -> dict:
        """
        Generate and persist explanation for a prediction.
        
        Steps:
          1. Build prompt from agent_outputs using PromptBuilder
          2. Call Grok LLM via LLMClient
          3. On failure: call FallbackBuilder
          4. Persist to prediction_explanations table
          5. Return explanation dict
        
        TODO: Implement per SPEC Section 14
        """
        raise NotImplementedError
