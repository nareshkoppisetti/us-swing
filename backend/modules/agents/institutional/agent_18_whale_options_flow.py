"""Agent 18 — Whale Options Flow | Institutional | Tier 2 | depends: [21,22]"""
import time, logging, numpy as np
from datetime import datetime
from modules.agents.base_agent import BaseAgent, AgentOutput, Signal
logger = logging.getLogger("agents")

class Agent18(BaseAgent):
    agent_id=18; agent_name="Whale Options Flow"; category="Institutional"
    refresh_frequency="hourly"; dependencies=[21,22]; tier=2

    def run(self, symbol, context):
        start = time.time()
        try:
            from modules.market_data.service import MarketDataService
            svc = MarketDataService()
            calls_df, puts_df = svc.get_options_chain(symbol)

            if calls_df is None or calls_df.empty or puts_df is None or puts_df.empty:
                return AgentOutput(agent_id=self.agent_id,agent_name=self.agent_name,
                    signal=Signal.NEUTRAL,score=50.0,confidence=15.0,weight=0.5,
                    reasoning="No options chain data available",bullish_factors=[],bearish_factors=[],
                    supporting_data={},llm_ready_summary={"agent":self.agent_name,"signal":"Neutral","finding":"No options data"},
                    data_freshness=datetime.utcnow().isoformat(),execution_time_ms=int((time.time()-start)*1000))

            call_oi = float(calls_df["openInterest"].fillna(0).sum()) if "openInterest" in calls_df.columns else 0
            put_oi  = float(puts_df["openInterest"].fillna(0).sum())  if "openInterest" in puts_df.columns else 0
            call_vol= float(calls_df["volume"].fillna(0).sum()) if "volume" in calls_df.columns else 0
            put_vol = float(puts_df["volume"].fillna(0).sum())  if "volume" in puts_df.columns else 0

            pc_oi  = put_oi / (call_oi + 1e-9)
            pc_vol = put_vol / (call_vol + 1e-9)
            # Unusual call sweeps (large OI, high volume) = bullish
            unusual_call = call_vol > call_oi * 0.3 and call_vol > 10000
            unusual_put  = put_vol > put_oi * 0.3 and put_vol > 10000

            # PC ratio below 0.7 = bullish, above 1.2 = bearish
            if pc_vol < 0.7 and unusual_call:
                signal = Signal.BULLISH; score = 70.0
            elif pc_vol > 1.2 and unusual_put:
                signal = Signal.BEARISH; score = 30.0
            else:
                signal = Signal.NEUTRAL; score = 50 - (pc_vol - 1.0) * 15
                score = float(np.clip(score, 0, 100))

            bf  = [f"Low P/C vol ratio={pc_vol:.2f} — call flow dominates"] if pc_vol < 0.7 else []
            brf = [f"High P/C vol ratio={pc_vol:.2f} — put flow dominates"] if pc_vol > 1.2 else []
            if unusual_call: bf.append(f"Unusual call sweep: {call_vol:,.0f} contracts (OI={call_oi:,.0f})")
            if unusual_put:  brf.append(f"Unusual put sweep: {put_vol:,.0f} contracts (OI={put_oi:,.0f})")

            return AgentOutput(agent_id=self.agent_id,agent_name=self.agent_name,
                signal=signal,score=float(np.clip(score,0,100)),confidence=float(np.clip(35+abs(score-50)*0.6,0,80)),
                weight=0.65,reasoning=f"P/C_OI={pc_oi:.2f}, P/C_vol={pc_vol:.2f}, unusual_call={unusual_call}",
                bullish_factors=bf,bearish_factors=brf,
                supporting_data={"call_oi":call_oi,"put_oi":put_oi,"call_vol":call_vol,"put_vol":put_vol,
                                  "pc_oi_ratio":pc_oi,"pc_vol_ratio":pc_vol},
                llm_ready_summary={"agent":self.agent_name,"signal":signal.value,
                    "finding":f"P/C_vol={pc_vol:.2f}; call_vol={call_vol:,.0f}; unusual_call={unusual_call}"},
                data_freshness=datetime.utcnow().isoformat(),execution_time_ms=int((time.time()-start)*1000))
        except Exception as e:
            return AgentOutput(agent_id=self.agent_id,agent_name=self.agent_name,signal=Signal.NEUTRAL,
                score=50.0,confidence=0.0,weight=0.65,reasoning="",bullish_factors=[],bearish_factors=[],
                supporting_data={},llm_ready_summary={"agent":self.agent_name,"signal":"Neutral","finding":"Failed"},
                data_freshness="",execution_time_ms=int((time.time()-start)*1000),error=str(e))
