"""Agent 33 — Final Prediction Engine | Prediction Layer | Tier 1 | depends: [30,31,32]"""
import time, logging, numpy as np
from datetime import datetime
from modules.agents.base_agent import BaseAgent, AgentOutput, Signal
logger = logging.getLogger("agents")

HORIZONS = [2, 5, 10, 20, 30, 60]

class Agent33(BaseAgent):
    agent_id=33; agent_name="Final Prediction Engine"; category="Prediction Layer"
    refresh_frequency="per_run"; dependencies=[30,31,32]; tier=1

    def run(self, symbol, context):
        start = time.time()
        try:
            a30 = context.get(30); a31 = context.get(31); a32 = context.get(32)
            if not all([a30, a31, a32]): raise ValueError("Agents 30/31/32 required")

            composite       = a30.score
            horizon_scores  = a31.supporting_data.get("horizon_scores", {h: composite for h in HORIZONS})
            expected_rets   = a31.supporting_data.get("expected_returns", {})
            final_confidence= a32.score
            risk_level      = a32.supporting_data.get("risk_level", "Moderate")
            is_degraded     = a32.supporting_data.get("is_degraded", False)
            failed_count    = a32.supporting_data.get("failed_agents", 0)

            # Build per-horizon prediction rows
            predictions = []
            for h in HORIZONS:
                s = horizon_scores.get(h, composite)
                er = expected_rets.get(h, 0)
                if s >= 60:   direction = "Bullish"
                elif s <= 40: direction = "Bearish"
                else:         direction = "Neutral"
                predictions.append({
                    "horizon_days": h,
                    "direction": direction,
                    "score": round(float(s), 2),
                    "expected_return_pct": round(float(er)*100, 2),
                    "confidence": round(float(final_confidence * (1 - (np.log(h)/np.log(60))*0.1)), 2),
                })

            overall_signal = a30.signal
            all_bullish = a30.bullish_factors[:5] + a31.bullish_factors[:3]
            all_bearish = a30.bearish_factors[:5] + a31.bearish_factors[:3]

            reasoning = (
                f"Final prediction for {symbol}: {overall_signal.value} with {final_confidence:.1f}% confidence. "
                f"Composite score={composite:.1f}/100. Risk={risk_level}. "
                f"{'[DEGRADED: >10 agents failed] ' if is_degraded else ''}"
                f"Horizons: " + "; ".join(f"{p['horizon_days']}d={p['direction']}({p['score']:.0f})" for p in predictions)
            )

            return AgentOutput(agent_id=self.agent_id, agent_name=self.agent_name,
                signal=overall_signal, score=composite, confidence=final_confidence,
                weight=1.0, reasoning=reasoning,
                bullish_factors=list(dict.fromkeys(all_bullish))[:8],
                bearish_factors=list(dict.fromkeys(all_bearish))[:8],
                supporting_data={
                    "symbol": symbol,
                    "predictions": predictions,
                    "composite_score": composite,
                    "final_confidence": final_confidence,
                    "risk_level": risk_level,
                    "is_degraded": is_degraded,
                    "failed_agents": failed_count,
                    "category_averages": a30.supporting_data.get("category_averages", {}),
                },
                llm_ready_summary={
                    "agent": self.agent_name,
                    "signal": overall_signal.value,
                    "finding": (
                        f"{symbol}: {overall_signal.value} | score={composite:.1f} | conf={final_confidence:.1f}% | "
                        f"risk={risk_level} | 5d={horizon_scores.get(5,50):.0f} 20d={horizon_scores.get(20,50):.0f} 60d={horizon_scores.get(60,50):.0f}"
                    ),
                },
                data_freshness=datetime.utcnow().isoformat(),
                execution_time_ms=int((time.time()-start)*1000))
        except Exception as e:
            logger.error(f"Agent33 failed for {symbol}: {e}")
            return AgentOutput(agent_id=self.agent_id,agent_name=self.agent_name,signal=Signal.NEUTRAL,
                score=50.0,confidence=0.0,weight=1.0,reasoning="",bullish_factors=[],bearish_factors=[],
                supporting_data={},llm_ready_summary={"agent":self.agent_name,"signal":"Neutral","finding":"Failed"},
                data_freshness="",execution_time_ms=int((time.time()-start)*1000),error=str(e))
