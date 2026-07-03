"""Agent 17 — 13F Accumulation | Institutional | Tier 1"""
import time, logging, numpy as np
from datetime import datetime
from modules.agents.base_agent import BaseAgent, AgentOutput, Signal
logger = logging.getLogger("agents")

class Agent17(BaseAgent):
    agent_id=17; agent_name="13F Accumulation"; category="Institutional"
    refresh_frequency="daily"; dependencies=[]; tier=1

    def run(self, symbol, context):
        start = time.time()
        try:
            from modules.market_data.collectors.sec_edgar_collector import SECEdgarCollector
            holdings = SECEdgarCollector().fetch_13f(symbol)
            count = len(holdings)
            score = 50 + min(count * 2, 20)  # more holders = slightly bullish
            signal = Signal.NEUTRAL
            if count > 15: signal = Signal.BULLISH; score = min(70, score)
            elif count == 0: score = 45.0

            return AgentOutput(agent_id=self.agent_id,agent_name=self.agent_name,
                signal=signal,score=float(np.clip(score,0,100)),confidence=float(min(40+count,75)),
                weight=0.7,reasoning=f"Found {count} institutional 13F filings for {symbol}",
                bullish_factors=[f"{count} institutional holders reported in 13F filings"] if count>5 else [],
                bearish_factors=["Few institutional 13F filings — limited institutional coverage"] if count<3 else [],
                supporting_data={"holder_count":count,"top_holders":holdings[:5]},
                llm_ready_summary={"agent":self.agent_name,"signal":signal.value,
                    "finding":f"13F filings: {count} institutional holders for {symbol}"},
                data_freshness=datetime.utcnow().isoformat(),execution_time_ms=int((time.time()-start)*1000))
        except Exception as e:
            return AgentOutput(agent_id=self.agent_id,agent_name=self.agent_name,signal=Signal.NEUTRAL,
                score=50.0,confidence=0.0,weight=0.7,reasoning="",bullish_factors=[],bearish_factors=[],
                supporting_data={},llm_ready_summary={"agent":self.agent_name,"signal":"Neutral","finding":"Failed"},
                data_freshness="",execution_time_ms=int((time.time()-start)*1000),error=str(e))
