"""Agent 25 — Relative Strength | Strength | Tier 1 | depends: [1,2]"""
import time, logging, numpy as np
from datetime import datetime
from modules.agents.base_agent import BaseAgent, AgentOutput, Signal
logger = logging.getLogger("agents")

class Agent25(BaseAgent):
    agent_id=25; agent_name="Relative Strength"; category="Strength"
    refresh_frequency="hourly"; dependencies=[1,2]; tier=1

    def run(self, symbol, context):
        start = time.time()
        try:
            from modules.market_data.service import MarketDataService
            svc = MarketDataService()
            df  = svc.get_ohlcv(symbol, period="6mo")
            spy = svc.get_ohlcv("SPY", period="6mo")
            if df is None or spy is None or len(df)<20: raise ValueError("Insufficient data")
            sym_ret_1m = (float(df["close"].iloc[-1]) / float(df["close"].iloc[-21]) - 1)*100 if len(df)>21 else 0
            spy_ret_1m = (float(spy["close"].iloc[-1]) / float(spy["close"].iloc[-21]) - 1)*100 if len(spy)>21 else 0
            sym_ret_3m = (float(df["close"].iloc[-1]) / float(df["close"].iloc[0]) - 1)*100
            spy_ret_3m = (float(spy["close"].iloc[-1]) / float(spy["close"].iloc[0]) - 1)*100

            rs_1m = sym_ret_1m - spy_ret_1m
            rs_3m = sym_ret_3m - spy_ret_3m
            rs_score = 50 + rs_1m * 2 + rs_3m * 0.5
            rs_score = float(np.clip(rs_score, 0, 100))
            signal = Signal.BULLISH if rs_score >= 58 else (Signal.BEARISH if rs_score <= 42 else Signal.NEUTRAL)

            return AgentOutput(agent_id=self.agent_id,agent_name=self.agent_name,
                signal=signal,score=rs_score,confidence=float(np.clip(35+abs(rs_score-50)*0.7,0,85)),
                weight=0.75,reasoning=f"{symbol} vs SPY: RS_1m={rs_1m:.1f}%, RS_3m={rs_3m:.1f}%",
                bullish_factors=[f"Outperforming SPY by {rs_1m:.1f}% (1m)"] if rs_1m>2 else [],
                bearish_factors=[f"Underperforming SPY by {abs(rs_1m):.1f}% (1m)"] if rs_1m<-2 else [],
                supporting_data={"sym_ret_1m":sym_ret_1m,"spy_ret_1m":spy_ret_1m,"rs_1m":rs_1m,"rs_3m":rs_3m},
                llm_ready_summary={"agent":self.agent_name,"signal":signal.value,
                    "finding":f"RS_1m={rs_1m:.1f}%; RS_3m={rs_3m:.1f}%; vs SPY"},
                data_freshness=datetime.utcnow().isoformat(),execution_time_ms=int((time.time()-start)*1000))
        except Exception as e:
            return AgentOutput(agent_id=self.agent_id,agent_name=self.agent_name,signal=Signal.NEUTRAL,
                score=50.0,confidence=0.0,weight=0.75,reasoning="",bullish_factors=[],bearish_factors=[],
                supporting_data={},llm_ready_summary={"agent":self.agent_name,"signal":"Neutral","finding":"Failed"},
                data_freshness="",execution_time_ms=int((time.time()-start)*1000),error=str(e))
