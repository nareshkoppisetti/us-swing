"""
File path: backend/modules/explainability/fallback_builder.py
Purpose: Template-based fallback narrative generator.
         Used when Grok LLM is unavailable or fails.
         Generates a structured, data-backed narrative from agent outputs
         without calling any external API.
         Per SPEC Section 14 (≥99% of predictions must have an explanation).

Fallback narrative template:
  "{symbol} shows a {direction} signal with {confidence}% confidence over the {horizon}-day horizon.
   Key bullish factors: {top_bullish_factor_1}, {top_bullish_factor_2}.
   Key bearish risks: {top_bearish_factor_1}.
   The market regime is {regime} with {breadth} breadth conditions.
   Signal strength is supported by {n_bullish}/{total} agents aligned {direction}."
"""
import logging
logger = logging.getLogger("app")


class FallbackNarrativeBuilder:
    """
    Generates a template-based explanation when LLM is unavailable.
    Always succeeds (no external calls).
    """

    def build(
        self,
        symbol: str,
        direction: str,
        confidence: float,
        risk_score: float,
        horizon_days: int,
        agent_outputs: dict,
        top_bullish: list,
        top_bearish: list,
    ) -> str:
        """
        Build a template-based analyst narrative.
        
        Returns:
            Narrative string (3-5 sentences, ≤2000 chars).
        
        TODO: Implement template filling with real agent data
        """
        # Placeholder template — replace with full data-driven implementation
        bullish_text = "; ".join(top_bullish[:2]) if top_bullish else "momentum alignment"
        bearish_text = "; ".join(top_bearish[:1]) if top_bearish else "macro uncertainty"
        
        total_agents = len(agent_outputs)
        bullish_agents = sum(
            1 for o in agent_outputs.values()
            if hasattr(o, "signal") and str(o.signal).lower() == "bullish"
        )

        return (
            f"{symbol} presents a {direction.lower()} signal with {confidence:.0f}% confidence "
            f"over the {horizon_days}-day horizon (risk score: {risk_score:.0f}/100). "
            f"Supporting bullish factors include: {bullish_text}. "
            f"Key risks to monitor: {bearish_text}. "
            f"Agent consensus: {bullish_agents}/{total_agents} agents aligned with the directional call. "
            f"[Auto-generated narrative — LLM unavailable]"
        )
