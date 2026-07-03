"""Agent 13 — Global Liquidity | Tier 2 | depends: [14]"""
import time, logging, numpy as np
from datetime import datetime
from modules.agents.base_agent import BaseAgent, AgentOutput, Signal
logger = logging.getLogger("agents")

class Agent13(BaseAgent):
    agent_id=13; agent_name="Global Liquidity"; category="News & Macro"
    refresh_frequency="daily"; dependencies=[14]; tier=2

    def run(self, symbol, context):
        start = time.time()
        try:
            from modules.market_data.service import MarketDataService
            svc = MarketDataService()
            # Liquidity proxies: TLT (bonds), HYG (high yield), USD (DXY)
            a14 = context.get(14)
            dxy_score = a14.score if (a14 and not a14.error) else 50.0

            tltscore = 50.0
            try:
                tlt = svc.get_ohlcv("TLT", period="3mo")
                if tlt is not None and len(tlt) >= 20:
                    close = tlt["close"].astype(float)
                    sma20 = float(close.rolling(20).mean().iloc[-1])
                    price = float(close.iloc[-1])
                    tltscore = 50 + (price/sma20 - 1) * 300
            except Exception: pass

            # DXY inverse relationship: strong USD = lower liquidity globally
            dxy_effect = 100 - dxy_score  # invert DXY signal
            liquidity_score = tltscore * 0.5 + dxy_effect * 0.5
            liquidity_score = float(np.clip(liquidity_score, 0, 100))
            signal = Signal.BULLISH if liquidity_score >= 58 else (Signal.BEARISH if liquidity_score <= 42 else Signal.NEUTRAL)

            return AgentOutput(agent_id=self.agent_id,agent_name=self.agent_name,
                signal=signal,score=liquidity_score,confidence=float(np.clip(30+abs(liquidity_score-50)*0.4,0,70)),
                weight=0.6,reasoning=f"Global liquidity proxy score={liquidity_score:.1f}; TLT={tltscore:.1f}; DXY_effect={dxy_effect:.1f}",
                bullish_factors=["TLT above 20-day MA — bond market bid (risk-on)"] if tltscore>55 else [],
                bearish_factors=["Strong USD constraining global liquidity"] if dxy_score>60 else [],
                supporting_data={"liquidity_score":liquidity_score,"tlt_score":tltscore,"dxy_effect":dxy_effect},
                llm_ready_summary={"agent":self.agent_name,"signal":signal.value,
                    "finding":f"Liquidity={liquidity_score:.0f}; TLT={tltscore:.0f}; DXY_inv={dxy_effect:.0f}"},
                data_freshness=datetime.utcnow().isoformat(),execution_time_ms=int((time.time()-start)*1000))
        except Exception as e:
            return AgentOutput(agent_id=self.agent_id,agent_name=self.agent_name,signal=Signal.NEUTRAL,
                score=50.0,confidence=0.0,weight=0.6,reasoning="",bullish_factors=[],bearish_factors=[],
                supporting_data={},llm_ready_summary={"agent":self.agent_name,"signal":"Neutral","finding":"Failed"},
                data_freshness="",execution_time_ms=int((time.time()-start)*1000),error=str(e))
