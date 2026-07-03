"""Agent 34 — Options OI Structure | Additional | Tier 1"""
import time, logging, numpy as np
from datetime import datetime
from modules.agents.base_agent import BaseAgent, AgentOutput, Signal
logger = logging.getLogger("agents")

class Agent34(BaseAgent):
    agent_id=34; agent_name="Options OI Structure"; category="Additional"
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
                    signal=Signal.NEUTRAL,score=50.0,confidence=10.0,weight=0.65,
                    reasoning="No options OI data available",bullish_factors=[],bearish_factors=[],
                    supporting_data={},llm_ready_summary={"agent":self.agent_name,"signal":"Neutral","finding":"No data"},
                    data_freshness=datetime.utcnow().isoformat(),execution_time_ms=int((time.time()-start)*1000))

            # Find max pain: strike where total OI loss is minimized
            all_strikes = []
            if "strike" in calls_df.columns:
                all_strikes = sorted(set(calls_df["strike"].dropna().tolist() +
                                         (puts_df["strike"].dropna().tolist() if "strike" in puts_df.columns else [])))

            max_pain = None
            min_loss = float("inf")
            for s in all_strikes:
                call_loss = float(calls_df[calls_df["strike"] >= s]["openInterest"].fillna(0).sum() *
                                   max(0, s - price)) if "strike" in calls_df.columns else 0
                put_loss  = float(puts_df[puts_df["strike"] <= s]["openInterest"].fillna(0).sum() *
                                   max(0, price - s)) if "strike" in puts_df.columns else 0
                total_loss = call_loss + put_loss
                if total_loss < min_loss:
                    min_loss = total_loss; max_pain = s

            # Call wall: highest call OI strike
            if "strike" in calls_df.columns and "openInterest" in calls_df.columns:
                call_wall_idx = calls_df["openInterest"].fillna(0).idxmax()
                call_wall = float(calls_df.loc[call_wall_idx, "strike"]) if call_wall_idx is not None else None
            else:
                call_wall = None

            mp_dist = ((max_pain - price) / price * 100) if max_pain and price > 0 else 0

            if mp_dist > 2: signal = Signal.BULLISH; score = 65.0
            elif mp_dist < -2: signal = Signal.BEARISH; score = 38.0
            else: signal = Signal.NEUTRAL; score = 50 + mp_dist * 5

            return AgentOutput(agent_id=self.agent_id,agent_name=self.agent_name,
                signal=signal,score=float(np.clip(score,0,100)),confidence=float(np.clip(30+min(len(all_strikes),20)*1.5,0,75)),
                weight=0.65,reasoning=f"Max pain={max_pain}, call wall={call_wall}, price={price:.2f}, dist={mp_dist:.1f}%",
                bullish_factors=[f"Price {abs(mp_dist):.1f}% below max pain — gravity pull up"] if mp_dist>2 else [],
                bearish_factors=[f"Price {abs(mp_dist):.1f}% above max pain — gravity pull down"] if mp_dist<-2 else [],
                supporting_data={"max_pain":max_pain,"call_wall":call_wall,"current_price":price,"max_pain_distance_pct":mp_dist},
                llm_ready_summary={"agent":self.agent_name,"signal":signal.value,
                    "finding":f"Max pain={max_pain}; call_wall={call_wall}; dist={mp_dist:.1f}%"},
                data_freshness=datetime.utcnow().isoformat(),execution_time_ms=int((time.time()-start)*1000))
        except Exception as e:
            return AgentOutput(agent_id=self.agent_id,agent_name=self.agent_name,signal=Signal.NEUTRAL,
                score=50.0,confidence=0.0,weight=0.65,reasoning="",bullish_factors=[],bearish_factors=[],
                supporting_data={},llm_ready_summary={"agent":self.agent_name,"signal":"Neutral","finding":"Failed"},
                data_freshness="",execution_time_ms=int((time.time()-start)*1000),error=str(e))
