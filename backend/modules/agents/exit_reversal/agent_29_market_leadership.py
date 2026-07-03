"""Agent 29 — Market Leadership | Exit & Reversal | Tier 1 | depends: [3,15]"""
import time, logging, numpy as np
from datetime import datetime
from modules.agents.base_agent import BaseAgent, AgentOutput, Signal
logger = logging.getLogger("agents")

class Agent29(BaseAgent):
    agent_id=29; agent_name="Market Leadership"; category="Exit & Reversal"
    refresh_frequency="daily"; dependencies=[3,15]; tier=1

    def run(self, symbol, context):
        start = time.time()
        try:
            a3  = context.get(3);  a15 = context.get(15)
            breadth_score  = (a3.score  if a3  and not a3.error  else 50)
            rotation_score = (a15.score if a15 and not a15.score else 50)
            from modules.market_data.service import MarketDataService
            svc = MarketDataService()
            df  = svc.get_ohlcv(symbol, period="3mo")
            spy = svc.get_ohlcv("SPY",    period="3mo")
            if df is None or spy is None or len(df)<20: raise ValueError("No data")
            sym_vol = float(df["close"].astype(float).pct_change().std())
            spy_vol = float(spy["close"].astype(float).pct_change().std())
            beta    = sym_vol / spy_vol if spy_vol > 0 else 1.0
            leadership_score = (breadth_score * 0.4 + rotation_score * 0.3 + (1/max(beta,0.5)) * 30)
            leadership_score = float(np.clip(leadership_score, 0, 100))
            signal = Signal.BULLISH if leadership_score >= 58 else (Signal.BEARISH if leadership_score <= 42 else Signal.NEUTRAL)

            return AgentOutput(agent_id=self.agent_id,agent_name=self.agent_name,
                signal=signal,score=leadership_score,confidence=float(np.clip(35+abs(leadership_score-50)*0.5,0,80)),
                weight=0.7,reasoning=f"Leadership score={leadership_score:.1f}; beta={beta:.2f}; breadth={breadth_score:.0f}",
                bullish_factors=[f"Beta={beta:.2f} — manageable market exposure; strong breadth={breadth_score:.0f}"] if leadership_score>58 else [],
                bearish_factors=[f"High beta ({beta:.2f}) with weak breadth ({breadth_score:.0f})"] if leadership_score<42 else [],
                supporting_data={"leadership_score":leadership_score,"beta":beta,"breadth_score":breadth_score},
                llm_ready_summary={"agent":self.agent_name,"signal":signal.value,
                    "finding":f"Leadership={leadership_score:.0f}; beta={beta:.2f}"},
                data_freshness=datetime.utcnow().isoformat(),execution_time_ms=int((time.time()-start)*1000))
        except Exception as e:
            return AgentOutput(agent_id=self.agent_id,agent_name=self.agent_name,signal=Signal.NEUTRAL,
                score=50.0,confidence=0.0,weight=0.7,reasoning="",bullish_factors=[],bearish_factors=[],
                supporting_data={},llm_ready_summary={"agent":self.agent_name,"signal":"Neutral","finding":"Failed"},
                data_freshness="",execution_time_ms=int((time.time()-start)*1000),error=str(e))
