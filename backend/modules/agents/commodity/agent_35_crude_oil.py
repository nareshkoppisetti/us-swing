"""Agent 35 — Crude Oil Intelligence | Commodity | Tier 1"""
import time, logging, numpy as np
from datetime import datetime
from modules.agents.base_agent import BaseAgent, AgentOutput, Signal
logger = logging.getLogger("agents")

class Agent35(BaseAgent):
    agent_id=35; agent_name="Crude Oil Intelligence"; category="Commodity"
    refresh_frequency="daily"; dependencies=[]; tier=1

    def run(self, symbol, context):
        start = time.time()
        try:
            from modules.market_data.service import MarketDataService
            from modules.market_data.collectors.eia_collector import EIACollector
            svc = MarketDataService()
            df = svc.get_ohlcv("CL=F", period="6mo")
            eia_data = EIACollector().fetch_petroleum_inventories()
            if df is None or len(df) < 20: raise ValueError("No crude data")
            close = df["close"].astype(float); price = float(close.iloc[-1])
            sma20 = float(close.rolling(20).mean().iloc[-1])
            ret_1m = (price / float(close.iloc[-21]) - 1) * 100 if len(close) > 21 else 0
            inv_change = float(eia_data.get("change") or 0)
            score = 50 + (price / sma20 - 1) * 200 + ret_1m * 2 - inv_change * 0.5
            score = float(np.clip(score, 0, 100))
            signal = Signal.BULLISH if score >= 58 else (Signal.BEARISH if score <= 42 else Signal.NEUTRAL)
            bf = [f"Crude draw: {abs(inv_change):.1f}M bbl from EIA"] if inv_change < 0 else []
            brf = [f"Crude build: +{inv_change:.1f}M bbl — bearish supply"] if inv_change > 2 else []
            if price > sma20: bf.append(f"WTI ${price:.1f} above 20-day MA")
            return AgentOutput(agent_id=self.agent_id, agent_name=self.agent_name,
                signal=signal, score=score, confidence=float(np.clip(40 + abs(score-50)*0.6, 0, 82)),
                weight=0.7, reasoning=f"WTI=${price:.1f}, SMA20=${sma20:.1f}, EIA_inv={inv_change:.1f}Mbbl",
                bullish_factors=bf, bearish_factors=brf,
                supporting_data={"crude_price":price,"sma20":sma20,"ret_1m":ret_1m,"eia_inv_change":inv_change},
                llm_ready_summary={"agent":self.agent_name,"signal":signal.value,
                    "finding":f"WTI=${price:.1f}; 1m={ret_1m:.1f}%; EIA_inv={inv_change:.1f}Mbbl"},
                data_freshness=datetime.utcnow().isoformat(), execution_time_ms=int((time.time()-start)*1000))
        except Exception as e:
            return AgentOutput(agent_id=self.agent_id,agent_name=self.agent_name,signal=Signal.NEUTRAL,
                score=50.0,confidence=0.0,weight=0.7,reasoning="",bullish_factors=[],bearish_factors=[],
                supporting_data={},llm_ready_summary={"agent":self.agent_name,"signal":"Neutral","finding":"Failed"},
                data_freshness="",execution_time_ms=int((time.time()-start)*1000),error=str(e))
