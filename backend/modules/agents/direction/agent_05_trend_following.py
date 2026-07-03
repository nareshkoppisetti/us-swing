"""Agent 05 — Trend Following | Direction | Tier 1 | depends: [2]"""
import time, logging, numpy as np
from datetime import datetime
from modules.agents.base_agent import BaseAgent, AgentOutput, Signal
logger = logging.getLogger("agents")

class Agent05(BaseAgent):
    agent_id=5; agent_name="Trend Following"; category="Direction"
    refresh_frequency="15min"; dependencies=[2]; tier=1

    def run(self, symbol, context):
        start = time.time()
        try:
            from modules.market_data.service import MarketDataService
            svc = MarketDataService()
            df = svc.get_ohlcv(symbol, period="1y")
            if df is None or len(df) < 20: raise ValueError("Insufficient data")
            close = df["close"].astype(float); high = df["high"].astype(float); low = df["low"].astype(float)
            vol   = df["volume"].astype(float)

            # Donchian Channel 20
            dc_upper = high.rolling(20).max()
            dc_lower = low.rolling(20).min()
            dc_upper_val = float(dc_upper.iloc[-1]); dc_lower_val = float(dc_lower.iloc[-1])
            price = float(close.iloc[-1])
            channel_pos = (price - dc_lower_val) / (dc_upper_val - dc_lower_val + 1e-9) * 100

            # Volume confirmation
            vol_avg20 = float(vol.rolling(20).mean().iloc[-1])
            vol_today = float(vol.iloc[-1])
            vol_ratio = vol_today / vol_avg20 if vol_avg20 > 0 else 1.0

            # 52-week high/low proximity
            hi52 = float(high.rolling(min(252, len(high))).max().iloc[-1])
            lo52 = float(low.rolling(min(252, len(low))).min().iloc[-1])
            proximity = (price - lo52) / (hi52 - lo52 + 1e-9) * 100

            # Breakout signal
            breakout_up   = price >= dc_upper_val * 0.995 and vol_ratio > 1.5
            breakout_down = price <= dc_lower_val * 1.005 and vol_ratio > 1.5

            score = channel_pos * 0.5 + proximity * 0.3 + (65 if breakout_up else 35 if breakout_down else 50) * 0.2
            score = float(np.clip(score, 0, 100))

            signal = Signal.BULLISH if score >= 60 else (Signal.BEARISH if score <= 40 else Signal.NEUTRAL)
            bf, brf = [], []
            if breakout_up:   bf.append(f"Bullish Donchian breakout with {vol_ratio:.1f}x avg volume")
            if proximity > 75: bf.append(f"Price near 52-week high ({proximity:.0f}% of range)")
            if breakout_down: brf.append(f"Bearish Donchian breakdown with {vol_ratio:.1f}x avg volume")
            if proximity < 25: brf.append(f"Price near 52-week low ({proximity:.0f}% of range)")

            return AgentOutput(agent_id=self.agent_id,agent_name=self.agent_name,
                signal=signal,score=score,confidence=float(np.clip(40+abs(score-50)*0.8,0,88)),
                weight=0.75,reasoning=f"Channel pos={channel_pos:.0f}%, vol_ratio={vol_ratio:.1f}x, 52w proximity={proximity:.0f}%",
                bullish_factors=bf,bearish_factors=brf,
                supporting_data={"dc_upper":dc_upper_val,"dc_lower":dc_lower_val,"channel_position":channel_pos,
                                  "volume_ratio":vol_ratio,"breakout_up":breakout_up,"breakout_down":breakout_down,
                                  "week52_proximity":proximity},
                llm_ready_summary={"agent":self.agent_name,"signal":signal.value,
                    "finding":f"Channel pos={channel_pos:.0f}%; breakout={'up' if breakout_up else 'down' if breakout_down else 'none'}; vol={vol_ratio:.1f}x"},
                data_freshness=datetime.utcnow().isoformat(),execution_time_ms=int((time.time()-start)*1000))
        except Exception as e:
            logger.error(f"Agent05 failed: {e}")
            return AgentOutput(agent_id=self.agent_id,agent_name=self.agent_name,signal=Signal.NEUTRAL,
                score=50.0,confidence=0.0,weight=0.75,reasoning="",bullish_factors=[],bearish_factors=[],
                supporting_data={},llm_ready_summary={"agent":self.agent_name,"signal":"Neutral","finding":"Failed"},
                data_freshness="",execution_time_ms=int((time.time()-start)*1000),error=str(e))
