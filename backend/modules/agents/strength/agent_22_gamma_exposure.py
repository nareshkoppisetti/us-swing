"""Agent 22 — Gamma Exposure | Strength | Tier 1"""
import time, logging, numpy as np
from datetime import datetime
from modules.agents.base_agent import BaseAgent, AgentOutput, Signal
logger = logging.getLogger("agents")

class Agent22(BaseAgent):
    agent_id=22; agent_name="Gamma Exposure"; category="Strength"
    refresh_frequency="hourly"; dependencies=[]; tier=1

    def run(self, symbol, context):
        start = time.time()
        try:
            from modules.market_data.service import MarketDataService
            svc = MarketDataService()
            calls_df, puts_df = svc.get_options_chain(symbol)
            quote = svc.get_quote(symbol)
            price = float(quote.get("price") or 0)

            if calls_df is None or calls_df.empty or price == 0:
                return AgentOutput(agent_id=self.agent_id,agent_name=self.agent_name,
                    signal=Signal.NEUTRAL,score=50.0,confidence=15.0,weight=0.7,
                    reasoning="No options data for gamma calculation",bullish_factors=[],bearish_factors=[],
                    supporting_data={},llm_ready_summary={"agent":self.agent_name,"signal":"Neutral","finding":"No data"},
                    data_freshness=datetime.utcnow().isoformat(),execution_time_ms=int((time.time()-start)*1000))

            # Simplified GEX: calls with strike near ATM
            atm_range = price * 0.02
            if "strike" in calls_df.columns and "openInterest" in calls_df.columns:
                calls_df = calls_df.copy()
                calls_df["atm"] = (calls_df["strike"] - price).abs() < atm_range
                atm_call_oi = float(calls_df[calls_df["atm"]]["openInterest"].fillna(0).sum())
                total_call_oi = float(calls_df["openInterest"].fillna(0).sum())
            else:
                atm_call_oi, total_call_oi = 0, 1

            gex_ratio = atm_call_oi / (total_call_oi + 1e-9)
            # High ATM call concentration = pinning = muted moves (neutral)
            # Low GEX = trend acceleration likely
            score = 50.0 + (gex_ratio - 0.1) * 50
            score = float(np.clip(score, 0, 100))
            signal = Signal.NEUTRAL  # GEX is primarily about volatility, not direction

            return AgentOutput(agent_id=self.agent_id,agent_name=self.agent_name,
                signal=signal,score=score,confidence=float(np.clip(30+gex_ratio*40,0,75)),
                weight=0.65,reasoning=f"GEX ratio={gex_ratio:.3f}; ATM call OI={atm_call_oi:,.0f}",
                bullish_factors=["Low GEX — market maker hedging may amplify upside"] if gex_ratio<0.05 else [],
                bearish_factors=["High ATM gamma — price likely to pin near this level"] if gex_ratio>0.3 else [],
                supporting_data={"gex_ratio":gex_ratio,"atm_call_oi":atm_call_oi,"total_call_oi":total_call_oi,"price":price},
                llm_ready_summary={"agent":self.agent_name,"signal":signal.value,
                    "finding":f"GEX ratio={gex_ratio:.3f}; ATM_OI={atm_call_oi:,.0f}"},
                data_freshness=datetime.utcnow().isoformat(),execution_time_ms=int((time.time()-start)*1000))
        except Exception as e:
            return AgentOutput(agent_id=self.agent_id,agent_name=self.agent_name,signal=Signal.NEUTRAL,
                score=50.0,confidence=0.0,weight=0.65,reasoning="",bullish_factors=[],bearish_factors=[],
                supporting_data={},llm_ready_summary={"agent":self.agent_name,"signal":"Neutral","finding":"Failed"},
                data_freshness="",execution_time_ms=int((time.time()-start)*1000),error=str(e))
