"""Agent 32 — Confidence Scoring | Prediction Layer | Tier 1 | depends: [30,31]"""
import time, logging, numpy as np
from datetime import datetime
from modules.agents.base_agent import BaseAgent, AgentOutput, Signal
logger = logging.getLogger("agents")

class Agent32(BaseAgent):
    agent_id=32; agent_name="Confidence Scoring"; category="Prediction Layer"
    refresh_frequency="per_run"; dependencies=[30,31]; tier=1

    def run(self, symbol, context):
        start = time.time()
        try:
            a30 = context.get(30); a31 = context.get(31)
            if not a30: raise ValueError("Agent 30 required")

            failed_count   = a30.supporting_data.get("failed_agents", 0)
            agents_used    = a30.supporting_data.get("agents_used", 42)
            avg_confidence = a30.supporting_data.get("avg_confidence", 50)
            composite      = a30.score
            horizon_scores = a31.supporting_data.get("horizon_scores", {}) if a31 and not a31.error else {}

            # Signal agreement ratio: how many horizons agree with direction
            if horizon_scores:
                if composite >= 58:
                    agree = sum(1 for s in horizon_scores.values() if s >= 55) / len(horizon_scores)
                elif composite <= 42:
                    agree = sum(1 for s in horizon_scores.values() if s <= 45) / len(horizon_scores)
                else:
                    agree = 0.5
            else:
                agree = 0.5

            # Confidence formula per SPEC:
            # base = avg_confidence of passing agents
            # penalty = 2 pts per failed agent
            # agreement bonus = up to +10
            # signal_strength bonus = proportional to distance from 50
            base_conf = avg_confidence
            failure_penalty = failed_count * 2
            agreement_bonus = agree * 10
            strength_bonus  = abs(composite - 50) * 0.4
            is_degraded     = failed_count > 10

            final_conf = float(np.clip(base_conf - failure_penalty + agreement_bonus + strength_bonus, 5, 95))

            # Risk level
            if final_conf >= 70: risk_level = "Low"
            elif final_conf >= 50: risk_level = "Moderate"
            else: risk_level = "High"

            score = final_conf
            signal = a30.signal

            return AgentOutput(agent_id=self.agent_id, agent_name=self.agent_name,
                signal=signal, score=score, confidence=final_conf,
                weight=1.0,
                reasoning=f"Confidence={final_conf:.1f}: base={base_conf:.1f}, fail_penalty=-{failure_penalty:.1f}, "
                           f"agree_bonus=+{agreement_bonus:.1f}, strength=+{strength_bonus:.1f}. Risk={risk_level}",
                bullish_factors=[f"Signal agreement: {agree:.0%} of horizons agree"] if agree > 0.7 else [],
                bearish_factors=[f"{failed_count} agents failed — reduced confidence"] if failed_count > 5 else [],
                supporting_data={"final_confidence":final_conf,"failure_penalty":failure_penalty,
                                  "agreement_ratio":agree,"is_degraded":is_degraded,
                                  "risk_level":risk_level,"failed_agents":failed_count},
                llm_ready_summary={"agent":self.agent_name,"signal":signal.value,
                    "finding":f"Confidence={final_conf:.1f}; risk={risk_level}; agree={agree:.0%}; failed={failed_count}"},
                data_freshness=datetime.utcnow().isoformat(),execution_time_ms=int((time.time()-start)*1000))
        except Exception as e:
            logger.error(f"Agent32 failed: {e}")
            return AgentOutput(agent_id=self.agent_id,agent_name=self.agent_name,signal=Signal.NEUTRAL,
                score=50.0,confidence=0.0,weight=1.0,reasoning="",bullish_factors=[],bearish_factors=[],
                supporting_data={},llm_ready_summary={"agent":self.agent_name,"signal":"Neutral","finding":"Failed"},
                data_freshness="",execution_time_ms=int((time.time()-start)*1000),error=str(e))
