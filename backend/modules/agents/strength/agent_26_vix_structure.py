"""Agent 26 — VIX Structure | Strength | Tier 1"""
import time, logging, numpy as np
from datetime import datetime
from modules.agents.base_agent import BaseAgent, AgentOutput, Signal
logger = logging.getLogger("agents")

class Agent26(BaseAgent):
    agent_id=26; agent_name="VIX Structure"; category="Strength"
    refresh_frequency="hourly"; dependencies=[]; tier=1

    def run(self, symbol, context):
        start = time.time()
        try:
            from modules.market_data.service import MarketDataService
            svc = MarketDataService()
            vix_data = svc.get_vix_data()
            vix = vix_data.get("vix") or 20.0
            vix9d = vix_data.get("vix9d")
            vix3m = vix_data.get("vix3m")
            ts = vix_data.get("term_structure", "unknown")
            score = 50 + (25 - vix) * 1.2
            if ts == "contango":   score += 10
            elif ts == "backwardation": score -= 15
            score = float(np.clip(score, 0, 100))
            signal = Signal.BULLISH if score >= 58 else (Signal.BEARISH if score <= 38 else Signal.NEUTRAL)

            return AgentOutput(agent_id=self.agent_id,agent_name=self.agent_name,
                signal=signal,score=score,confidence=float(np.clip(45+abs(score-50)*0.5,0,85)),
                weight=0.8,reasoning=f"VIX={vix:.1f}, VIX9D={vix9d}, VIX3M={vix3m}, structure={ts}",
                bullish_factors=[f"VIX contango (VIX9D < VIX3M) — calm near-term outlook"] if ts=="contango" else [],
                bearish_factors=[f"VIX backwardation — near-term fear elevated; VIX={vix:.1f}"] if ts=="backwardation" or vix>25 else [],
                supporting_data={"vix":vix,"vix9d":vix9d,"vix3m":vix3m,"term_structure":ts},
                llm_ready_summary={"agent":self.agent_name,"signal":signal.value,
                    "finding":f"VIX={vix:.1f}; structure={ts}; score={score:.0f}"},
                data_freshness=datetime.utcnow().isoformat(),execution_time_ms=int((time.time()-start)*1000))
        except Exception as e:
            return AgentOutput(agent_id=self.agent_id,agent_name=self.agent_name,signal=Signal.NEUTRAL,
                score=50.0,confidence=0.0,weight=0.8,reasoning="",bullish_factors=[],bearish_factors=[],
                supporting_data={},llm_ready_summary={"agent":self.agent_name,"signal":"Neutral","finding":"Failed"},
                data_freshness="",execution_time_ms=int((time.time()-start)*1000),error=str(e))
