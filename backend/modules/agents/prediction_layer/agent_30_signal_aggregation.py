"""Agent 30 — Signal Aggregation | Prediction Layer | Tier 1 | depends: all 1-29, 34-42"""
import time, logging, numpy as np
from datetime import datetime
from modules.agents.base_agent import BaseAgent, AgentOutput, Signal
logger = logging.getLogger("agents")

CATEGORY_WEIGHTS = {
    "Direction":        0.25,
    "News & Macro":     0.18,
    "Institutional":    0.18,
    "Strength":         0.17,
    "Exit & Reversal":  0.10,
    "Additional":       0.07,
    "Commodity":        0.05,
}
ALL_DEPS = list(range(1, 30)) + [34] + list(range(35, 43))

class Agent30(BaseAgent):
    agent_id=30; agent_name="Signal Aggregation"; category="Prediction Layer"
    refresh_frequency="per_run"; dependencies=ALL_DEPS; tier=1

    def run(self, symbol, context):
        start = time.time()
        try:
            category_scores = {}
            category_confidences = {}
            all_bullish, all_bearish = [], []

            for agent_id, output in context.items():
                if not output or output.error or output.confidence < 5:
                    continue
                cat = output.agent_name  # placeholder — use category from output
                # Map agent_id to category
                if agent_id <= 6:   cat = "Direction"
                elif agent_id <= 14: cat = "News & Macro"
                elif agent_id <= 20: cat = "Institutional"
                elif agent_id <= 26: cat = "Strength"
                elif agent_id <= 29: cat = "Exit & Reversal"
                elif agent_id == 34: cat = "Additional"
                else:               cat = "Commodity"

                w = output.weight * (output.confidence / 100.0)
                if cat not in category_scores:
                    category_scores[cat] = []
                    category_confidences[cat] = []
                category_scores[cat].append(output.score * w)
                category_confidences[cat].append(w)
                all_bullish.extend(output.bullish_factors)
                all_bearish.extend(output.bearish_factors)

            # Weighted average per category
            cat_avg = {}
            for cat, scores in category_scores.items():
                total_w = sum(category_confidences[cat])
                cat_avg[cat] = sum(scores) / total_w if total_w > 0 else 50.0

            # Apply category weights
            composite = 0.0; total_w = 0.0
            for cat, avg in cat_avg.items():
                cw = CATEGORY_WEIGHTS.get(cat, 0.1)
                composite += avg * cw
                total_w += cw

            composite = composite / total_w if total_w > 0 else 50.0
            composite = float(np.clip(composite, 0, 100))

            signal = Signal.BULLISH if composite >= 58 else (Signal.BEARISH if composite <= 42 else Signal.NEUTRAL)
            failed = sum(1 for o in context.values() if o and o.error)
            avg_conf = float(np.mean([o.confidence for o in context.values() if o and not o.error])) if context else 50.0

            return AgentOutput(agent_id=self.agent_id, agent_name=self.agent_name,
                signal=signal, score=composite, confidence=float(np.clip(avg_conf - failed*2, 5, 95)),
                weight=1.0,
                reasoning=f"Weighted composite from {len(context)} agents ({failed} failed). Category breakdown: " +
                    "; ".join(f"{c}={v:.1f}" for c,v in cat_avg.items()),
                bullish_factors=list(set(all_bullish))[:8],
                bearish_factors=list(set(all_bearish))[:8],
                supporting_data={"composite_score":composite,"category_averages":cat_avg,
                                  "agents_used":len(context),"failed_agents":failed,"avg_confidence":avg_conf},
                llm_ready_summary={"agent":self.agent_name,"signal":signal.value,
                    "finding":f"Composite={composite:.1f}; {len(context)} agents; {failed} failed; avg_conf={avg_conf:.1f}"},
                data_freshness=datetime.utcnow().isoformat(),execution_time_ms=int((time.time()-start)*1000))
        except Exception as e:
            logger.error(f"Agent30 failed: {e}")
            return AgentOutput(agent_id=self.agent_id,agent_name=self.agent_name,signal=Signal.NEUTRAL,
                score=50.0,confidence=0.0,weight=1.0,reasoning="",bullish_factors=[],bearish_factors=[],
                supporting_data={},llm_ready_summary={"agent":self.agent_name,"signal":"Neutral","finding":"Failed"},
                data_freshness="",execution_time_ms=int((time.time()-start)*1000),error=str(e))
