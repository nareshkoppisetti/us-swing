"""Agent 23 — Factor Crowding | Strength | Tier 2 | depends: [15,17]"""
import time, logging, numpy as np
from datetime import datetime
from modules.agents.base_agent import BaseAgent, AgentOutput, Signal
logger = logging.getLogger("agents")

class Agent23(BaseAgent):
    agent_id=23; agent_name="Factor Crowding"; category="Strength"
    refresh_frequency="daily"; dependencies=[15,17]; tier=2

    def run(self, symbol, context):
        start = time.time()
        try:
            from modules.market_data.service import MarketDataService
            svc = MarketDataService()
            # Growth vs value proxy: QQQ vs IWD
            qqq = svc.get_ohlcv("QQQ", period="3mo")
            iwd = svc.get_ohlcv("IWD", period="3mo")
            if qqq is None or iwd is None or len(qqq)<20: raise ValueError("No factor data")
            qqq_ret = (float(qqq["close"].iloc[-1]) / float(qqq["close"].iloc[-21]) - 1)*100 if len(qqq)>21 else 0
            iwd_ret = (float(iwd["close"].iloc[-1]) / float(iwd["close"].iloc[-21]) - 1)*100 if len(iwd)>21 else 0
            growth_value_spread = qqq_ret - iwd_ret
            # Large positive spread = growth momentum (crowding risk)
            crowding_score = 50 + growth_value_spread * 1.5
            crowding_score = float(np.clip(crowding_score, 0, 100))
            signal = Signal.NEUTRAL if abs(crowding_score-50) < 10 else (Signal.BULLISH if crowding_score>55 else Signal.BEARISH)

            return AgentOutput(agent_id=self.agent_id,agent_name=self.agent_name,
                signal=signal,score=crowding_score,confidence=float(np.clip(30+abs(growth_value_spread)*1.5,0,70)),
                weight=0.55,reasoning=f"Growth/Value spread (1m): QQQ={qqq_ret:.1f}% vs IWD={iwd_ret:.1f}%; spread={growth_value_spread:.1f}%",
                bullish_factors=[f"Growth outperforming value by {growth_value_spread:.1f}% — momentum factor"] if growth_value_spread>3 else [],
                bearish_factors=[f"Growth crowding risk: {growth_value_spread:.1f}% spread may revert"] if growth_value_spread>8 else [],
                supporting_data={"qqq_1m_return":qqq_ret,"iwd_1m_return":iwd_ret,"growth_value_spread":growth_value_spread},
                llm_ready_summary={"agent":self.agent_name,"signal":signal.value,
                    "finding":f"G/V spread={growth_value_spread:.1f}%; QQQ={qqq_ret:.1f}%; IWD={iwd_ret:.1f}%"},
                data_freshness=datetime.utcnow().isoformat(),execution_time_ms=int((time.time()-start)*1000))
        except Exception as e:
            return AgentOutput(agent_id=self.agent_id,agent_name=self.agent_name,signal=Signal.NEUTRAL,
                score=50.0,confidence=0.0,weight=0.55,reasoning="",bullish_factors=[],bearish_factors=[],
                supporting_data={},llm_ready_summary={"agent":self.agent_name,"signal":"Neutral","finding":"Failed"},
                data_freshness="",execution_time_ms=int((time.time()-start)*1000),error=str(e))
