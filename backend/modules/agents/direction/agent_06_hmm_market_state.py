"""Agent 06 — HMM Market State | Tier 2 | depends: [1,2] | MVP: rule-based state machine"""
import time, logging, numpy as np
from datetime import datetime
from modules.agents.base_agent import BaseAgent, AgentOutput, Signal
logger = logging.getLogger("agents")

class Agent06(BaseAgent):
    agent_id=6; agent_name="HMM Market State"; category="Direction"
    refresh_frequency="hourly"; dependencies=[1,2]; tier=2

    def run(self, symbol, context):
        start = time.time()
        try:
            a1 = context.get(1); a2 = context.get(2)
            # MVP rule-based state machine (full HMM in production)
            if a1 and a2 and not a1.error and not a2.error:
                r_score = a1.score; t_score = a2.score
                bull_prob = (r_score/100 * 0.6 + t_score/100 * 0.4)
                bear_prob = ((100-r_score)/100 * 0.5 + (100-t_score)/100 * 0.5)
                side_prob = 1.0 - bull_prob - bear_prob
                side_prob = max(0, side_prob)
                norm = bull_prob + bear_prob + side_prob
                bull_prob /= norm; bear_prob /= norm; side_prob /= norm
            else:
                bull_prob, bear_prob, side_prob = 0.34, 0.33, 0.33

            if bull_prob > bear_prob and bull_prob > side_prob:
                state = "Bull"; signal = Signal.BULLISH; score = bull_prob * 100
            elif bear_prob > bull_prob and bear_prob > side_prob:
                state = "Bear"; signal = Signal.BEARISH; score = (1-bear_prob)*100
            else:
                state = "Sideways"; signal = Signal.NEUTRAL; score = 50.0

            return AgentOutput(agent_id=self.agent_id,agent_name=self.agent_name,
                signal=signal,score=float(np.clip(score,0,100)),confidence=float(np.clip(50+abs(score-50)*0.5,0,80)),
                weight=0.6,reasoning=f"HMM state={state} (MVP rule-based). Bull={bull_prob:.2f}, Bear={bear_prob:.2f}, Sideways={side_prob:.2f}",
                bullish_factors=[f"Bull state probability: {bull_prob:.1%}"] if bull_prob>0.5 else [],
                bearish_factors=[f"Bear state probability: {bear_prob:.1%}"] if bear_prob>0.5 else [],
                supporting_data={"hmm_state":state,"bull_probability":bull_prob,"bear_probability":bear_prob,"sideways_probability":side_prob},
                llm_ready_summary={"agent":self.agent_name,"signal":signal.value,
                    "finding":f"HMM state={state}; bull_prob={bull_prob:.2f}; bear_prob={bear_prob:.2f}"},
                data_freshness=datetime.utcnow().isoformat(),execution_time_ms=int((time.time()-start)*1000))
        except Exception as e:
            return AgentOutput(agent_id=self.agent_id,agent_name=self.agent_name,signal=Signal.NEUTRAL,
                score=50.0,confidence=0.0,weight=0.6,reasoning="",bullish_factors=[],bearish_factors=[],
                supporting_data={},llm_ready_summary={"agent":self.agent_name,"signal":"Neutral","finding":"Failed"},
                data_freshness="",execution_time_ms=int((time.time()-start)*1000),error=str(e))
