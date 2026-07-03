"""Agent 08 — Earnings Sentiment | News & Macro | Tier 1"""
import time, logging, numpy as np
from datetime import datetime, date
from modules.agents.base_agent import BaseAgent, AgentOutput, Signal
logger = logging.getLogger("agents")

class Agent08(BaseAgent):
    agent_id=8; agent_name="Earnings Sentiment"; category="News & Macro"
    refresh_frequency="daily"; dependencies=[]; tier=1

    def run(self, symbol, context):
        start = time.time()
        try:
            from modules.market_data.collectors.yahoo_collector import YahooFinanceCollector
            yc = YahooFinanceCollector()
            earnings = yc.fetch_earnings(symbol)
            next_date_str = earnings.get("next_earnings_date")
            history = earnings.get("history", [])

            days_to_earnings = 999
            if next_date_str:
                try:
                    next_dt = datetime.strptime(str(next_date_str)[:10], "%Y-%m-%d").date()
                    days_to_earnings = (next_dt - date.today()).days
                    if days_to_earnings < 0: days_to_earnings = 999
                except Exception: pass

            # Earnings risk score: higher = more risk
            if days_to_earnings <= 1: risk = 90
            elif days_to_earnings <= 3: risk = 70
            elif days_to_earnings <= 7: risk = 45
            elif days_to_earnings <= 14: risk = 25
            else: risk = 5

            # Surprise average from history
            surprises = [h.get("surprise_pct",0) or 0 for h in history if h.get("surprise_pct") is not None]
            surprise_avg = float(np.mean(surprises)) if surprises else 0.0

            # Score: positive surprise history is bullish; high risk reduces confidence
            score = 50 + float(np.clip(surprise_avg * 2, -20, 20)) - risk * 0.1
            score = float(np.clip(score, 0, 100))
            signal = Signal.BULLISH if score >= 58 and risk < 50 else (Signal.BEARISH if score <= 42 else Signal.NEUTRAL)
            conf = max(20, 60 - risk * 0.4)

            bf = [f"Avg EPS surprise: +{surprise_avg:.1f}%"] if surprise_avg > 5 else []
            brf = [f"Earnings in {days_to_earnings} days — elevated uncertainty"] if days_to_earnings <= 7 else []
            if surprise_avg < -5: brf.append(f"Avg EPS miss: {surprise_avg:.1f}%")

            return AgentOutput(agent_id=self.agent_id,agent_name=self.agent_name,
                signal=signal,score=score,confidence=float(np.clip(conf,0,80)),weight=0.75,
                reasoning=f"Days to earnings={days_to_earnings}, surprise_avg={surprise_avg:.1f}%, risk={risk}",
                bullish_factors=bf,bearish_factors=brf,
                supporting_data={"days_to_earnings":days_to_earnings,"surprise_average":surprise_avg,"earnings_risk_score":risk},
                llm_ready_summary={"agent":self.agent_name,"signal":signal.value,
                    "finding":f"Earnings in {days_to_earnings}d; avg surprise={surprise_avg:.1f}%; risk={risk}"},
                data_freshness=datetime.utcnow().isoformat(),execution_time_ms=int((time.time()-start)*1000))
        except Exception as e:
            return AgentOutput(agent_id=self.agent_id,agent_name=self.agent_name,signal=Signal.NEUTRAL,
                score=50.0,confidence=0.0,weight=0.75,reasoning="",bullish_factors=[],bearish_factors=[],
                supporting_data={},llm_ready_summary={"agent":self.agent_name,"signal":"Neutral","finding":"Failed"},
                data_freshness="",execution_time_ms=int((time.time()-start)*1000),error=str(e))
