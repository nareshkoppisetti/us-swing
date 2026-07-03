"""
File path: backend/modules/explainability/prompt_builder.py
Purpose: ExplanationPromptBuilder — assembles structured prompts for Grok LLM.
         Converts agent outputs into a concise, data-rich prompt for narrative generation.
         Per SPEC Section 14.

Prompt structure:
  System: "You are an institutional equity research analyst..."
  User:   Structured JSON context with:
            - symbol, prediction direction, confidence, horizon
            - top 3 bullish factors (with data values)
            - top 3 bearish factors (with data values)
            - key agent findings (llm_ready_summary from each agent, max 200 chars each)
            - market regime, macro context
         Request: "Generate a 3-5 sentence analyst narrative..."

Output narrative: 3-5 sentences, institutional tone, data-backed, max 2000 chars.
"""
import logging
logger = logging.getLogger("app")


class ExplanationPromptBuilder:
    """
    Builds LLM prompts from prediction context and agent outputs.
    """

    SYSTEM_PROMPT = (
        "You are an institutional equity research analyst at a top-tier hedge fund. "
        "You write concise, data-backed market commentary in 3-5 sentences. "
        "Your tone is professional, precise, and avoids speculation without data support. "
        "Always reference specific data points (prices, percentages, indicators) when available."
    )

    def build(
        self,
        symbol: str,
        direction: str,
        confidence: float,
        horizon_days: int,
        agent_outputs: dict,
        top_bullish: list,
        top_bearish: list,
    ) -> tuple[str, str]:
        """
        Build system + user prompt pair for Grok.
        
        Returns:
            Tuple of (system_prompt: str, user_prompt: str)
        
        TODO: Implement
        Steps:
          1. Extract llm_ready_summary from each agent output
          2. Select top 3 bullish and bearish factors with supporting data
          3. Format as structured JSON context
          4. Append instruction to generate 3-5 sentence narrative
          5. Return (SYSTEM_PROMPT, formatted_user_prompt)
        """
        raise NotImplementedError("ExplanationPromptBuilder.build() not yet implemented")

    def _extract_top_factors(self, agent_outputs: dict, factor_type: str, n: int = 3) -> list[str]:
        """
        Extract top N bullish or bearish factors across all agents,
        sorted by agent score * weight (impact).
        """
        # TODO: Implement
        return []
