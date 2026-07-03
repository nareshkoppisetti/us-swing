"""Agent 31 — Ensemble Model | Prediction Layer | Tier 1 | depends: [30]"""
import time, logging, numpy as np
from datetime import datetime
from modules.agents.base_agent import BaseAgent, AgentOutput, Signal
logger = logging.getLogger("agents")

HORIZON_DAYS = [2, 5, 10, 20, 30, 60]

class Agent31(BaseAgent):
    agent_id=31; agent_name="Ensemble Model"; category="Prediction Layer"
    refresh_frequency="per_run"; dependencies=[30]; tier=1

    def run(self, symbol, context):
        start = time.time()
        try:
            a30 = context.get(30)
            if not a30 or a30.error: raise ValueError("Agent 30 output required")
            composite = a30.score
            cat_avgs = a30.supporting_data.get("category_averages", {})

            # Per-horizon predictions: shorter horizons more influenced by momentum/news
            # Longer horizons more influenced by macro/institutional
            horizon_scores = {}
            for h in HORIZON_DAYS:
                if h <= 5:    # Short-term: momentum + news dominant
                    base = (cat_avgs.get("Direction",50)*0.35 + cat_avgs.get("News & Macro",50)*0.35 +
                            cat_avgs.get("Strength",50)*0.30)
                elif h <= 20: # Medium-term: balanced
                    base = composite
                else:         # Long-term: macro + institutional
                    base = (cat_avgs.get("News & Macro",50)*0.3 + cat_avgs.get("Institutional",50)*0.35 +
                            cat_avgs.get("Direction",50)*0.2 + cat_avgs.get("Strength",50)*0.15)

                # Add noise adjustment for longer horizons (less certainty)
                horizon_decay = 1.0 - (np.log(h)/np.log(60))*0.15
                horizon_scores[h] = float(np.clip(base * horizon_decay + (1-horizon_decay)*50, 0, 100))

            # Expected return per horizon (simplified)
            returns = {}
            for h, s in horizon_scores.items():
                expected_ret = (s - 50) / 100 * (h ** 0.5) * 0.5
                returns[h] = round(float(expected_ret), 3)

            ensemble_score = float(np.mean(list(horizon_scores.values())))
            signal = Signal.BULLISH if ensemble_score >= 58 else (Signal.BEARISH if ensemble_score <= 42 else Signal.NEUTRAL)

            return AgentOutput(agent_id=self.agent_id, agent_name=self.agent_name,
                signal=signal, score=ensemble_score,
                confidence=float(np.clip(a30.confidence * 0.95, 5, 90)),
                weight=1.0,
                reasoning=f"Ensemble across {len(HORIZON_DAYS)} horizons. Scores: " +
                    "; ".join(f"{h}d={s:.1f}" for h,s in horizon_scores.items()),
                bullish_factors=[f"{h}d score={s:.1f} (bullish)" for h,s in horizon_scores.items() if s>=58],
                bearish_factors=[f"{h}d score={s:.1f} (bearish)" for h,s in horizon_scores.items() if s<=42],
                supporting_data={"horizon_scores":horizon_scores,"expected_returns":returns,"ensemble_score":ensemble_score},
                llm_ready_summary={"agent":self.agent_name,"signal":signal.value,
                    "finding":f"Ensemble={ensemble_score:.1f}; 2d={horizon_scores[2]:.1f}; 20d={horizon_scores[20]:.1f}; 60d={horizon_scores[60]:.1f}"},
                data_freshness=datetime.utcnow().isoformat(),execution_time_ms=int((time.time()-start)*1000))
        except Exception as e:
            logger.error(f"Agent31 failed: {e}")
            return AgentOutput(agent_id=self.agent_id,agent_name=self.agent_name,signal=Signal.NEUTRAL,
                score=50.0,confidence=0.0,weight=1.0,reasoning="",bullish_factors=[],bearish_factors=[],
                supporting_data={},llm_ready_summary={"agent":self.agent_name,"signal":"Neutral","finding":"Failed"},
                data_freshness="",execution_time_ms=int((time.time()-start)*1000),error=str(e))
