"""Agent 27 — Correlation Decay | Exit & Reversal | Tier 2 | depends: [28]"""
import time, logging, numpy as np
from datetime import datetime
from modules.agents.base_agent import BaseAgent, AgentOutput, Signal
logger = logging.getLogger("agents")

class Agent27(BaseAgent):
    agent_id=27; agent_name="Correlation Decay"; category="Exit & Reversal"
    refresh_frequency="daily"; dependencies=[28]; tier=2

    def run(self, symbol, context):
        start = time.time()
        try:
            a28 = context.get(28)
            spy_corr = a28.supporting_data.get("spy_correlation",0.7) if (a28 and not a28.error) else 0.7
            recent_corr = a28.supporting_data.get("rolling_30d_corr",spy_corr) if (a28 and not a28.error) else spy_corr
            corr_decay = float(spy_corr) - float(recent_corr) if recent_corr else 0.0

            if corr_decay > 0.2:
                signal = Signal.BULLISH; score = 65.0
                finding = f"Correlation decaying ({corr_decay:.2f}) — {symbol} decoupling from SPY (potential outperformer)"
            elif corr_decay < -0.2:
                signal = Signal.BEARISH; score = 38.0
                finding = f"Correlation rising ({abs(corr_decay):.2f}) — increasing market dependency"
            else:
                signal = Signal.NEUTRAL; score = 50.0
                finding = f"Correlation stable (decay={corr_decay:.2f})"

            return AgentOutput(agent_id=self.agent_id,agent_name=self.agent_name,
                signal=signal,score=float(np.clip(score,0,100)),confidence=float(np.clip(30+abs(corr_decay)*100,0,70)),
                weight=0.55,reasoning=finding,
                bullish_factors=[finding] if signal==Signal.BULLISH else [],
                bearish_factors=[finding] if signal==Signal.BEARISH else [],
                supporting_data={"correlation_decay":corr_decay,"long_term_corr":spy_corr,"recent_corr":recent_corr},
                llm_ready_summary={"agent":self.agent_name,"signal":signal.value,"finding":finding[:200]},
                data_freshness=datetime.utcnow().isoformat(),execution_time_ms=int((time.time()-start)*1000))
        except Exception as e:
            return AgentOutput(agent_id=self.agent_id,agent_name=self.agent_name,signal=Signal.NEUTRAL,
                score=50.0,confidence=0.0,weight=0.55,reasoning="",bullish_factors=[],bearish_factors=[],
                supporting_data={},llm_ready_summary={"agent":self.agent_name,"signal":"Neutral","finding":"Failed"},
                data_freshness="",execution_time_ms=int((time.time()-start)*1000),error=str(e))
