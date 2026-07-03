"""Agent 02 — Trend Structure | Direction | Tier 1"""
import time, logging, numpy as np
from datetime import datetime
from modules.agents.base_agent import BaseAgent, AgentOutput, Signal
logger = logging.getLogger("agents")

class Agent02(BaseAgent):
    agent_id=2; agent_name="Trend Structure"; category="Direction"
    refresh_frequency="15min"; dependencies=[]; tier=1

    def run(self, symbol, context):
        start = time.time()
        try:
            from modules.market_data.service import MarketDataService
            svc = MarketDataService()
            df = svc.get_ohlcv(symbol, period="1y")
            if df is None or len(df) < 50: raise ValueError("Insufficient data")
            close = df["close"].astype(float)
            ema8   = close.ewm(span=8, adjust=False).mean()
            ema21  = close.ewm(span=21, adjust=False).mean()
            ema50  = close.ewm(span=50, adjust=False).mean()
            ema200 = close.ewm(span=200, adjust=False).mean()

            e8,e21,e50,e200 = float(ema8.iloc[-1]),float(ema21.iloc[-1]),float(ema50.iloc[-1]),float(ema200.iloc[-1])
            price = float(close.iloc[-1])
            above_ema200 = price > e200

            # Alignment score: count bullish alignments
            aligns = [(e8>e21),(e21>e50),(e50>e200),(price>e50),(price>e200)]
            bull_aligns = sum(aligns)
            alignment_score = bull_aligns / len(aligns) * 100

            # Golden/Death cross detection (recent 10 bars)
            golden_cross = bool((ema50.iloc[-10:-1] < ema200.iloc[-10:-1]).any() and ema50.iloc[-1] > ema200.iloc[-1])
            death_cross  = bool((ema50.iloc[-10:-1] > ema200.iloc[-10:-1]).any() and ema50.iloc[-1] < ema200.iloc[-1])

            # Trend slope via linear regression on last 20 close values
            y = close.iloc[-20:].values
            x = np.arange(len(y))
            slope = float(np.polyfit(x, y, 1)[0])
            slope_pct = slope / float(close.iloc[-20]) * 100

            # Score and signal
            score = alignment_score
            if golden_cross: score = min(100, score + 15)
            if death_cross: score = max(0, score - 15)

            signal = Signal.BULLISH if score >= 60 else (Signal.BEARISH if score <= 40 else Signal.NEUTRAL)
            bf, brf = [], []
            if bull_aligns >= 4: bf.append(f"Strong EMA alignment ({bull_aligns}/5 bullish)")
            if above_ema200: bf.append(f"Price {(price/e200-1)*100:.1f}% above EMA200")
            if golden_cross: bf.append("Golden Cross: EMA50 crossed above EMA200")
            if slope_pct > 0: bf.append(f"20-day trend slope: +{slope_pct:.2f}%/bar")
            if bull_aligns <= 2: brf.append(f"Weak EMA alignment ({bull_aligns}/5 bullish)")
            if not above_ema200: brf.append(f"Price below EMA200 by {(1-price/e200)*100:.1f}%")
            if death_cross: brf.append("Death Cross: EMA50 crossed below EMA200")
            if slope_pct < 0: brf.append(f"20-day trend slope: {slope_pct:.2f}%/bar")

            return AgentOutput(agent_id=self.agent_id, agent_name=self.agent_name,
                signal=signal, score=float(np.clip(score,0,100)), confidence=min(85, 35+score*0.5),
                weight=0.85, reasoning=f"EMA alignment {bull_aligns}/5; slope={slope_pct:.2f}%/bar; GC={golden_cross}; DC={death_cross}",
                bullish_factors=bf, bearish_factors=brf,
                supporting_data={"ema8":e8,"ema21":e21,"ema50":e50,"ema200":e200,"golden_cross":golden_cross,
                                  "death_cross":death_cross,"price_above_ema200":above_ema200,"slope_pct":slope_pct},
                llm_ready_summary={"agent":self.agent_name,"signal":signal.value,
                    "finding":f"EMA align {bull_aligns}/5; GC={golden_cross}; slope={slope_pct:.2f}%/bar"},
                data_freshness=datetime.utcnow().isoformat(), execution_time_ms=int((time.time()-start)*1000))
        except Exception as e:
            logger.error(f"Agent02 failed for {symbol}: {e}")
            return AgentOutput(agent_id=self.agent_id,agent_name=self.agent_name,signal=Signal.NEUTRAL,
                score=50.0,confidence=0.0,weight=0.85,reasoning="",bullish_factors=[],bearish_factors=[],
                supporting_data={},llm_ready_summary={"agent":self.agent_name,"signal":"Neutral","finding":"Failed"},
                data_freshness="",execution_time_ms=int((time.time()-start)*1000),error=str(e))
