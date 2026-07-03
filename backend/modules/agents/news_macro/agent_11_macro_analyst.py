"""Agent 11 — Macro Analyst | News & Macro | Tier 1"""
import time, logging, numpy as np
from datetime import datetime
from modules.agents.base_agent import BaseAgent, AgentOutput, Signal
logger = logging.getLogger("agents")

class Agent11(BaseAgent):
    agent_id=11; agent_name="Macro Analyst"; category="News & Macro"
    refresh_frequency="daily"; dependencies=[]; tier=1

    def run(self, symbol, context):
        start = time.time()
        try:
            from modules.market_data.collectors.fred_collector import FREDCollector
            fred = FREDCollector()
            dgs10 = fred.fetch_series("DGS10", limit=5)
            dgs2  = fred.fetch_series("DGS2",  limit=5)
            cpi   = fred.fetch_series("CPIAUCSL", limit=3)
            unrate= fred.fetch_series("UNRATE",   limit=3)

            yield10 = float(dgs10.iloc[-1]) if len(dgs10)>0 else 4.5
            yield2  = float(dgs2.iloc[-1])  if len(dgs2)>0  else 4.8
            spread  = yield10 - yield2
            cpi_val = float(cpi.iloc[-1])   if len(cpi)>0   else 3.0
            unemp   = float(unrate.iloc[-1]) if len(unrate)>0 else 4.0

            # Yield curve: positive = normal, negative = inverted
            curve_score = 50 + spread * 10
            # CPI: below 3% = bullish, above 4% = bearish
            cpi_score   = 70 - (cpi_val - 2.5) * 8
            # Unemployment: below 4% = bullish
            unemp_score = 75 - (unemp - 3.5) * 10
            macro_score = curve_score*0.4 + cpi_score*0.35 + unemp_score*0.25
            macro_score = float(np.clip(macro_score, 0, 100))

            signal = Signal.BULLISH if macro_score >= 58 else (Signal.BEARISH if macro_score <= 42 else Signal.NEUTRAL)
            bf, brf = [], []
            if spread > 0:   bf.append(f"Yield curve positive: {spread:.2f}% (10Y-2Y)")
            if cpi_val < 3:  bf.append(f"CPI={cpi_val:.1f}% — inflation controlled")
            if unemp < 4.0:  bf.append(f"Unemployment={unemp:.1f}% — strong labor market")
            if spread < -0.2:brf.append(f"Yield curve inverted: {spread:.2f}% — recession risk")
            if cpi_val > 4:  brf.append(f"CPI={cpi_val:.1f}% — elevated inflation")
            if unemp > 5:    brf.append(f"Unemployment={unemp:.1f}% — labor market weakening")

            return AgentOutput(agent_id=self.agent_id,agent_name=self.agent_name,
                signal=signal,score=macro_score,confidence=float(np.clip(50+abs(macro_score-50)*0.5,20,85)),
                weight=0.75,reasoning=f"Yield spread={spread:.2f}%, CPI={cpi_val:.1f}%, UNRATE={unemp:.1f}%",
                bullish_factors=bf,bearish_factors=brf,
                supporting_data={"yield_10y":yield10,"yield_2y":yield2,"yield_spread":spread,"cpi":cpi_val,"unemployment":unemp},
                llm_ready_summary={"agent":self.agent_name,"signal":signal.value,
                    "finding":f"Yield spread={spread:.2f}%; CPI={cpi_val:.1f}%; UNRATE={unemp:.1f}%"},
                data_freshness=datetime.utcnow().isoformat(),execution_time_ms=int((time.time()-start)*1000))
        except Exception as e:
            logger.error(f"Agent11 failed: {e}")
            return AgentOutput(agent_id=self.agent_id,agent_name=self.agent_name,signal=Signal.NEUTRAL,
                score=50.0,confidence=0.0,weight=0.75,reasoning="",bullish_factors=[],bearish_factors=[],
                supporting_data={},llm_ready_summary={"agent":self.agent_name,"signal":"Neutral","finding":"Failed"},
                data_freshness="",execution_time_ms=int((time.time()-start)*1000),error=str(e))
