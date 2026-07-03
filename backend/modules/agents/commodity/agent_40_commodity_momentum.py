"""Agent 40 — Commodity Momentum | Commodity | Tier 1 | depends: [35, 36, 37, 38, 39]"""
import time, logging, numpy as np
from datetime import datetime
from modules.agents.base_agent import BaseAgent, AgentOutput, Signal
logger = logging.getLogger("agents")

class Agent40(BaseAgent):
    agent_id=40; agent_name="Commodity Momentum"; category="Commodity"
    refresh_frequency="daily"; dependencies=[35, 36, 37, 38, 39]; tier=1

    def run(self, symbol, context):
        start = time.time()
        try:
            dep_scores = [context[d].score for d in [35, 36, 37, 38, 39] if d in context and context[d] and not context[d].error]
            score = float(np.mean(dep_scores)) if dep_scores else 50.0
            signal = Signal.BULLISH if score>=58 else (Signal.BEARISH if score<=42 else Signal.NEUTRAL)
            return AgentOutput(agent_id=self.agent_id, agent_name=self.agent_name,
                signal=signal, score=score, confidence=float(np.clip(30+len(dep_scores)*8,0,78)),
                weight=0.65, reasoning=f"Commodity Momentum: composite from {len(dep_scores)} upstream agents. Score={score:.1f}",
                bullish_factors=[f"Commodity composite bullish ({score:.0f}/100)"] if score>=58 else [],
                bearish_factors=[f"Commodity composite bearish ({score:.0f}/100)"] if score<=42 else [],
                supporting_data={"composite_score":score,"agents_used":len(dep_scores)},
                llm_ready_summary={"agent":self.agent_name,"signal":signal.value,"finding":f"Composite={score:.0f}; {len(dep_scores)} upstream"},
                data_freshness=datetime.utcnow().isoformat(), execution_time_ms=int((time.time()-start)*1000))
        except Exception as e:
            return AgentOutput(agent_id=self.agent_id,agent_name=self.agent_name,signal=Signal.NEUTRAL,
                score=50.0,confidence=0.0,weight=0.65,reasoning="",bullish_factors=[],bearish_factors=[],
                supporting_data={},llm_ready_summary={"agent":self.agent_name,"signal":"Neutral","finding":"Failed"},
                data_freshness="",execution_time_ms=int((time.time()-start)*1000),error=str(e))
