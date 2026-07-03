"""Agent 03 — Market Breadth | Direction | Tier 1"""
import time, logging, numpy as np
from datetime import datetime
from modules.agents.base_agent import BaseAgent, AgentOutput, Signal
logger = logging.getLogger("agents")
SECTOR_ETFS = ["XLK","XLF","XLE","XLV","XLI","XLY","XLP","XLRE","XLU","XLB","XLC"]

class Agent03(BaseAgent):
    agent_id=3; agent_name="Market Breadth"; category="Direction"
    refresh_frequency="15min"; dependencies=[]; tier=1

    def run(self, symbol, context):
        start = time.time()
        try:
            from modules.market_data.service import MarketDataService
            svc = MarketDataService()
            above_20, above_50, above_200, up_today = 0, 0, 0, 0
            total = 0
            for etf in SECTOR_ETFS:
                try:
                    df = svc.get_ohlcv(etf, period="1y")
                    if df is None or len(df) < 20: continue
                    close = df["close"].astype(float)
                    price = float(close.iloc[-1])
                    ma20  = float(close.rolling(20).mean().iloc[-1])
                    ma50  = float(close.rolling(50).mean().iloc[-1]) if len(close)>=50 else ma20
                    ma200 = float(close.rolling(200).mean().iloc[-1]) if len(close)>=200 else ma50
                    prev  = float(close.iloc[-2])
                    if price > ma20: above_20 += 1
                    if price > ma50: above_50 += 1
                    if price > ma200: above_200 += 1
                    if price > prev: up_today += 1
                    total += 1
                except Exception: pass

            if total == 0: raise ValueError("No sector ETF data available")
            pct20  = above_20 / total * 100
            pct50  = above_50 / total * 100
            pct200 = above_200 / total * 100
            adv_dec = up_today / total * 100

            breadth_score = pct20*0.5 + pct50*0.3 + pct200*0.2
            signal = Signal.BULLISH if breadth_score >= 60 else (Signal.BEARISH if breadth_score <= 40 else Signal.NEUTRAL)
            conf = 40 + abs(breadth_score - 50) * 0.8

            bf = [f"{pct20:.0f}% of sector ETFs above 20-day MA"] if pct20 > 60 else []
            if pct200 > 70: bf.append(f"{pct200:.0f}% above 200-day MA — broad bull market")
            brf = [f"Only {pct20:.0f}% above 20-day MA — weak breadth"] if pct20 < 40 else []
            if pct200 < 30: brf.append(f"{100-pct200:.0f}% of ETFs below 200-day MA")

            return AgentOutput(agent_id=self.agent_id,agent_name=self.agent_name,
                signal=signal,score=float(np.clip(breadth_score,0,100)),confidence=float(np.clip(conf,0,90)),
                weight=0.8,reasoning=f"Breadth: {pct20:.0f}%>20d, {pct50:.0f}%>50d, {pct200:.0f}%>200d, adv/dec={adv_dec:.0f}%",
                bullish_factors=bf,bearish_factors=brf,
                supporting_data={"pct_above_20d":pct20,"pct_above_50d":pct50,"pct_above_200d":pct200,
                                  "adv_dec_ratio":adv_dec,"total_etfs":total},
                llm_ready_summary={"agent":self.agent_name,"signal":signal.value,
                    "finding":f"Breadth score={breadth_score:.0f}; {pct20:.0f}%>20d; {pct200:.0f}%>200d"},
                data_freshness=datetime.utcnow().isoformat(),execution_time_ms=int((time.time()-start)*1000))
        except Exception as e:
            logger.error(f"Agent03 failed: {e}")
            return AgentOutput(agent_id=self.agent_id,agent_name=self.agent_name,signal=Signal.NEUTRAL,
                score=50.0,confidence=0.0,weight=0.8,reasoning="",bullish_factors=[],bearish_factors=[],
                supporting_data={},llm_ready_summary={"agent":self.agent_name,"signal":"Neutral","finding":"Failed"},
                data_freshness="",execution_time_ms=int((time.time()-start)*1000),error=str(e))
