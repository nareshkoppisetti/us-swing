"""Agent 21 — Put/Call Parity | Strength | Tier 1"""
import time, logging, numpy as np
from datetime import datetime
from modules.agents.base_agent import BaseAgent, AgentOutput, Signal
logger = logging.getLogger("agents")

class Agent21(BaseAgent):
    agent_id=21; agent_name="Put Call Parity"; category="Strength"
    refresh_frequency="hourly"; dependencies=[]; tier=1

    def run(self, symbol, context):
        start = time.time()
        try:
            from modules.market_data.service import MarketDataService
            svc = MarketDataService()
            calls_df, puts_df = svc.get_options_chain(symbol)
            if calls_df is None or calls_df.empty: raise ValueError("No options chain")

            call_oi  = float(calls_df["openInterest"].fillna(0).sum()) if "openInterest" in calls_df.columns else 0
            put_oi   = float(puts_df["openInterest"].fillna(0).sum())  if "openInterest" in puts_df.columns else 0
            call_vol = float(calls_df["volume"].fillna(0).sum()) if "volume" in calls_df.columns else 0
            put_vol  = float(puts_df["volume"].fillna(0).sum())  if "volume" in puts_df.columns else 0

            pc_oi  = put_oi / (call_oi + 1e-9)
            pc_vol = put_vol / (call_vol + 1e-9)

            # Score: pc_ratio < 0.7 = bullish (more calls), > 1.3 = bearish (more puts)
            score = 100 - (pc_vol / 2.0 * 100)
            score = float(np.clip(score, 0, 100))
            signal = Signal.BULLISH if score >= 60 else (Signal.BEARISH if score <= 40 else Signal.NEUTRAL)

            return AgentOutput(agent_id=self.agent_id,agent_name=self.agent_name,
                signal=signal,score=score,confidence=float(np.clip(35+abs(score-50)*0.7,0,85)),
                weight=0.75,reasoning=f"P/C OI ratio={pc_oi:.2f}, P/C vol ratio={pc_vol:.2f}",
                bullish_factors=[f"P/C volume ratio={pc_vol:.2f} — call dominance"] if pc_vol<0.7 else [],
                bearish_factors=[f"P/C volume ratio={pc_vol:.2f} — put protection buying"] if pc_vol>1.2 else [],
                supporting_data={"pc_oi_ratio":pc_oi,"pc_vol_ratio":pc_vol,"call_oi":call_oi,"put_oi":put_oi},
                llm_ready_summary={"agent":self.agent_name,"signal":signal.value,
                    "finding":f"P/C_OI={pc_oi:.2f}; P/C_vol={pc_vol:.2f}; score={score:.0f}"},
                data_freshness=datetime.utcnow().isoformat(),execution_time_ms=int((time.time()-start)*1000))
        except Exception as e:
            return AgentOutput(agent_id=self.agent_id,agent_name=self.agent_name,signal=Signal.NEUTRAL,
                score=50.0,confidence=0.0,weight=0.75,reasoning="",bullish_factors=[],bearish_factors=[],
                supporting_data={},llm_ready_summary={"agent":self.agent_name,"signal":"Neutral","finding":"Failed"},
                data_freshness="",execution_time_ms=int((time.time()-start)*1000),error=str(e))
