"""Agent 12 — Federal Reserve | News & Macro | Tier 1 | depends: [11]"""
import time, logging, numpy as np
from datetime import datetime
from modules.agents.base_agent import BaseAgent, AgentOutput, Signal
logger = logging.getLogger("agents")

class Agent12(BaseAgent):
    agent_id=12; agent_name="Federal Reserve"; category="News & Macro"
    refresh_frequency="daily"; dependencies=[11]; tier=1

    def run(self, symbol, context):
        start = time.time()
        try:
            from modules.market_data.collectors.fred_collector import FREDCollector
            fred = FREDCollector()
            fed_funds = fred.fetch_series("FEDFUNDS", limit=6)
            m2        = fred.fetch_series("M2SL",    limit=6)

            rate = float(fed_funds.iloc[-1]) if len(fed_funds)>0 else 5.25
            rate_prev = float(fed_funds.iloc[-2]) if len(fed_funds)>1 else rate
            rate_change = rate - rate_prev

            m2_now = float(m2.iloc[-1])  if len(m2)>0 else 1.0
            m2_prev= float(m2.iloc[-3])  if len(m2)>2 else m2_now
            m2_growth = (m2_now/m2_prev - 1)*100 if m2_prev != 0 else 0.0

            a11 = context.get(11)
            cpi = a11.supporting_data.get("cpi", 3.0) if (a11 and not a11.error) else 3.0

            # Real rate = fed funds - CPI
            real_rate = rate - cpi
            # Dovish: low real rate, falling rate, M2 growing
            # Hawkish: high real rate, rising rate, M2 contracting
            fed_score = 50.0
            if rate_change < 0:   fed_score += 15   # rate cut = bullish
            elif rate_change > 0: fed_score -= 15   # rate hike = bearish
            if real_rate < 0:     fed_score += 10   # negative real rate = stimulative
            elif real_rate > 2:   fed_score -= 10   # high real rate = restrictive
            if m2_growth > 3:     fed_score += 8
            elif m2_growth < 0:   fed_score -= 8

            fed_score = float(np.clip(fed_score, 0, 100))
            signal = Signal.BULLISH if fed_score >= 58 else (Signal.BEARISH if fed_score <= 42 else Signal.NEUTRAL)

            bf  = [f"Fed rate cut: {rate:.2f}% (down {abs(rate_change):.2f}%)"] if rate_change < 0 else []
            if real_rate < 0: bf.append(f"Negative real rate ({real_rate:.2f}%) — accommodative policy")
            brf = [f"Fed rate hike: {rate:.2f}% (+{rate_change:.2f}%)"] if rate_change > 0 else []
            if real_rate > 2: brf.append(f"High real rate ({real_rate:.2f}%) — restrictive policy")

            return AgentOutput(agent_id=self.agent_id,agent_name=self.agent_name,
                signal=signal,score=fed_score,confidence=float(np.clip(40+abs(fed_score-50)*0.6,0,85)),
                weight=0.8,reasoning=f"Fed funds={rate:.2f}%, change={rate_change:+.2f}%, real_rate={real_rate:.2f}%, M2_growth={m2_growth:.1f}%",
                bullish_factors=bf,bearish_factors=brf,
                supporting_data={"fed_funds_rate":rate,"rate_change":rate_change,"real_rate":real_rate,"m2_growth_pct":m2_growth},
                llm_ready_summary={"agent":self.agent_name,"signal":signal.value,
                    "finding":f"Fed={rate:.2f}%; change={rate_change:+.2f}%; real={real_rate:.2f}%; M2={m2_growth:.1f}%"},
                data_freshness=datetime.utcnow().isoformat(),execution_time_ms=int((time.time()-start)*1000))
        except Exception as e:
            return AgentOutput(agent_id=self.agent_id,agent_name=self.agent_name,signal=Signal.NEUTRAL,
                score=50.0,confidence=0.0,weight=0.8,reasoning="",bullish_factors=[],bearish_factors=[],
                supporting_data={},llm_ready_summary={"agent":self.agent_name,"signal":"Neutral","finding":"Failed"},
                data_freshness="",execution_time_ms=int((time.time()-start)*1000),error=str(e))
