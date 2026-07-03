"""Agent 19 — Insider Transactions | Institutional | Tier 1"""
import time, logging, numpy as np
from datetime import datetime
from modules.agents.base_agent import BaseAgent, AgentOutput, Signal
logger = logging.getLogger("agents")

class Agent19(BaseAgent):
    agent_id=19; agent_name="Insider Transactions"; category="Institutional"
    refresh_frequency="daily"; dependencies=[]; tier=1

    def run(self, symbol, context):
        start = time.time()
        try:
            from modules.market_data.collectors.sec_edgar_collector import SECEdgarCollector
            txns = SECEdgarCollector().fetch_form4(symbol, days=30)
            buys = [t for t in txns if t.get("transaction_type") == "purchase"]
            sells= [t for t in txns if t.get("transaction_type") == "sale"]
            net = len(buys) - len(sells)
            score = 50 + net * 5
            score = float(np.clip(score, 0, 100))
            signal = Signal.BULLISH if net > 0 else (Signal.BEARISH if net < 0 else Signal.NEUTRAL)

            return AgentOutput(agent_id=self.agent_id,agent_name=self.agent_name,
                signal=signal,score=score,confidence=float(min(30+len(txns)*2,75)),
                weight=0.75,reasoning=f"Insider: {len(buys)} buys, {len(sells)} sells in last 30 days",
                bullish_factors=[f"{len(buys)} insider purchases in 30d"] if buys else [],
                bearish_factors=[f"{len(sells)} insider sales in 30d"] if sells else [],
                supporting_data={"insider_buys":len(buys),"insider_sells":len(sells),"net":net,"transaction_count":len(txns)},
                llm_ready_summary={"agent":self.agent_name,"signal":signal.value,
                    "finding":f"Insider 30d: {len(buys)} buys, {len(sells)} sells, net={net}"},
                data_freshness=datetime.utcnow().isoformat(),execution_time_ms=int((time.time()-start)*1000))
        except Exception as e:
            return AgentOutput(agent_id=self.agent_id,agent_name=self.agent_name,signal=Signal.NEUTRAL,
                score=50.0,confidence=0.0,weight=0.75,reasoning="",bullish_factors=[],bearish_factors=[],
                supporting_data={},llm_ready_summary={"agent":self.agent_name,"signal":"Neutral","finding":"Failed"},
                data_freshness="",execution_time_ms=int((time.time()-start)*1000),error=str(e))
