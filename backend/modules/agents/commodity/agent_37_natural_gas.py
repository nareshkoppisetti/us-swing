"""Agent 37 — Natural Gas Intelligence | Commodity | Tier 1"""
import time, logging, numpy as np
from datetime import datetime
from modules.agents.base_agent import BaseAgent, AgentOutput, Signal
logger = logging.getLogger("agents")

class Agent37(BaseAgent):
    agent_id=37; agent_name="Natural Gas Intelligence"; category="Commodity"
    refresh_frequency="daily"; dependencies=[]; tier=1

    def run(self, symbol, context):
        start = time.time()
        try:
            from modules.market_data.service import MarketDataService
            svc = MarketDataService()
            df = svc.get_ohlcv("NG=F", period="6mo")
            if df is None or len(df) < 20: raise ValueError("No Natural Gas data")
            close = df["close"].astype(float)
            px = float(close.iloc[-1])
            sma20 = float(close.rolling(20).mean().iloc[-1])
            sma50 = float(close.rolling(50).mean().iloc[-1]) if len(close)>=50 else sma20
            ret_1m = (px / float(close.iloc[-21]) - 1) * 100 if len(close) > 21 else 0
            rsi = svc._compute_rsi(close, 14) or 50.0
            score = 50 + (px/sma20-1)*200 + ret_1m*1.5
            score = float(np.clip(score, 0, 100))
            signal = Signal.BULLISH if score>=58 else (Signal.BEARISH if score<=42 else Signal.NEUTRAL)
            bf = [f"Natural Gas above 20-day MA — bullish"] if px>sma20 else []
            brf= [f"Natural Gas below 20-day MA — bearish"] if px<sma20 else []
            if rsi > 70: brf.append(f"RSI={rsi:.1f} — Natural Gas overbought")
            if rsi < 30: bf.append(f"RSI={rsi:.1f} — oversold bounce potential")
            return AgentOutput(agent_id=self.agent_id, agent_name=self.agent_name,
                signal=signal, score=score, confidence=float(np.clip(35+abs(score-50)*0.6,0,82)),
                weight=0.7, reasoning=f"Natural Gas={px:.2f}, SMA20={sma20:.2f}, RSI={rsi:.1f}, 1m={ret_1m:.1f}%",
                bullish_factors=bf, bearish_factors=brf,
                supporting_data={"price":px,"sma20":sma20,"sma50":sma50,"rsi":rsi,"ret_1m":ret_1m},
                llm_ready_summary={"agent":self.agent_name,"signal":signal.value,
                    "finding":f"Natural Gas={px:.2f}; 1m={ret_1m:.1f}%; RSI={rsi:.1f}"},
                data_freshness=datetime.utcnow().isoformat(), execution_time_ms=int((time.time()-start)*1000))
        except Exception as e:
            return AgentOutput(agent_id=self.agent_id,agent_name=self.agent_name,signal=Signal.NEUTRAL,
                score=50.0,confidence=0.0,weight=0.7,reasoning="",bullish_factors=[],bearish_factors=[],
                supporting_data={},llm_ready_summary={"agent":self.agent_name,"signal":"Neutral","finding":"Failed"},
                data_freshness="",execution_time_ms=int((time.time()-start)*1000),error=str(e))
