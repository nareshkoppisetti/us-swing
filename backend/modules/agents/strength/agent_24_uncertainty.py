"""Agent 24 — Uncertainty | Strength | Tier 1 | depends: [26]"""
import time, logging, numpy as np
from datetime import datetime
from modules.agents.base_agent import BaseAgent, AgentOutput, Signal
logger = logging.getLogger("agents")

class Agent24(BaseAgent):
    agent_id=24; agent_name="Uncertainty"; category="Strength"
    refresh_frequency="hourly"; dependencies=[26]; tier=1

    def run(self, symbol, context):
        start = time.time()
        try:
            from modules.market_data.service import MarketDataService
            svc = MarketDataService()
            vix_data = svc.get_vix_data()
            vix = vix_data.get("vix") or 20.0
            a26 = context.get(26)
            term_structure = (a26.supporting_data.get("term_structure","unknown") if a26 and not a26.error else "unknown")

            # VIX levels: <15=low, 15-25=normal, 25-35=elevated, >35=crisis
            if vix < 15:
                unc_score = 75; desc = "Complacency"
            elif vix < 25:
                unc_score = 55; desc = "Normal"
            elif vix < 35:
                unc_score = 35; desc = "Elevated"
            else:
                unc_score = 15; desc = "Crisis"

            if term_structure == "contango": unc_score += 8
            elif term_structure == "backwardation": unc_score -= 12

            unc_score = float(np.clip(unc_score, 0, 100))
            signal = Signal.BULLISH if unc_score >= 60 else (Signal.BEARISH if unc_score <= 35 else Signal.NEUTRAL)

            return AgentOutput(agent_id=self.agent_id,agent_name=self.agent_name,
                signal=signal,score=unc_score,confidence=float(np.clip(50+abs(unc_score-50)*0.5,0,85)),
                weight=0.75,reasoning=f"VIX={vix:.1f} ({desc}); term_structure={term_structure}",
                bullish_factors=[f"VIX={vix:.1f} — low uncertainty environment"] if vix<20 else [],
                bearish_factors=[f"VIX={vix:.1f} — elevated market fear"] if vix>25 else [],
                supporting_data={"vix":vix,"vix_regime":desc,"term_structure":term_structure},
                llm_ready_summary={"agent":self.agent_name,"signal":signal.value,
                    "finding":f"VIX={vix:.1f} ({desc}); structure={term_structure}; score={unc_score:.0f}"},
                data_freshness=datetime.utcnow().isoformat(),execution_time_ms=int((time.time()-start)*1000))
        except Exception as e:
            return AgentOutput(agent_id=self.agent_id,agent_name=self.agent_name,signal=Signal.NEUTRAL,
                score=50.0,confidence=0.0,weight=0.75,reasoning="",bullish_factors=[],bearish_factors=[],
                supporting_data={},llm_ready_summary={"agent":self.agent_name,"signal":"Neutral","finding":"Failed"},
                data_freshness="",execution_time_ms=int((time.time()-start)*1000),error=str(e))
