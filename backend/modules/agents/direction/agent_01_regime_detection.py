"""
Agent 01 — Regime Detection | Direction | Tier 1 | 15min
Classify market regime: Trending-Up, Trending-Down, Range-Bound, Volatile, Transitional.
Inputs: Daily OHLCV (SPY + target symbol), ADX, ATR, rolling volatility
"""
import time
import logging
import numpy as np
from datetime import datetime
from modules.agents.base_agent import BaseAgent, AgentOutput, Signal

logger = logging.getLogger("agents")

class Agent01(BaseAgent):
    agent_id = 1
    agent_name = "Regime Detection"
    category = "Direction"
    refresh_frequency = "15min"
    dependencies = []
    tier = 1

    def run(self, symbol: str, context: dict) -> AgentOutput:
        start = time.time()
        try:
            from core.cache import init_cache, get_cache
            from modules.market_data.service import MarketDataService
            svc = MarketDataService()
            df = svc.get_ohlcv(symbol, period="1y")
            spy_df = svc.get_ohlcv("SPY", period="1y") if symbol != "SPY" else df

            if df is None or len(df) < 20:
                raise ValueError("Insufficient OHLCV data")

            close = df["close"].astype(float)
            high = df["high"].astype(float)
            low = df["low"].astype(float)

            adx = svc._compute_adx(high, low, close, 14) or 20.0
            vol_20 = float(close.pct_change().rolling(20).std().iloc[-1] or 0.01)
            vol_60 = float(close.pct_change().rolling(60).std().iloc[-1] or 0.01)
            vol_ratio = vol_20 / vol_60 if vol_60 > 0 else 1.0

            # Determine trend direction using EMA
            ema_50 = float(close.ewm(span=50).mean().iloc[-1])
            price = float(close.iloc[-1])
            price_vs_ema50 = (price - ema_50) / ema_50 * 100

            # Regime classification
            if adx > 25 and price_vs_ema50 > 0:
                regime = "Trending-Up"
                regime_score = min(100, 50 + adx * 0.8 + price_vs_ema50 * 2)
                signal = Signal.BULLISH
            elif adx > 25 and price_vs_ema50 < 0:
                regime = "Trending-Down"
                regime_score = max(0, 50 - adx * 0.8 + price_vs_ema50 * 2)
                signal = Signal.BEARISH
            elif vol_ratio > 1.3:
                regime = "Volatile"
                regime_score = 50 - (vol_ratio - 1.0) * 10
                signal = Signal.NEUTRAL
            elif adx < 20:
                regime = "Range-Bound"
                regime_score = 50.0
                signal = Signal.NEUTRAL
            else:
                regime = "Transitional"
                regime_score = 50.0 + price_vs_ema50
                signal = Signal.NEUTRAL

            regime_score = float(np.clip(regime_score, 0, 100))
            confidence = min(90, 40 + adx * 0.8 + abs(price_vs_ema50) * 1.5)

            bullish_factors, bearish_factors = [], []
            if adx > 25: bullish_factors.append(f"ADX={adx:.1f} confirms strong trend")
            if price_vs_ema50 > 2: bullish_factors.append(f"Price {price_vs_ema50:.1f}% above EMA50")
            if vol_ratio < 1.0: bullish_factors.append("Volatility stable vs 60-day baseline")
            if price_vs_ema50 < -2: bearish_factors.append(f"Price {abs(price_vs_ema50):.1f}% below EMA50")
            if vol_ratio > 1.3: bearish_factors.append(f"Volatility elevated: {vol_ratio:.2f}x 60-day avg")
            if adx < 20: bearish_factors.append(f"ADX={adx:.1f} — weak trend, ranging market")

            return AgentOutput(
                agent_id=self.agent_id, agent_name=self.agent_name,
                signal=signal, score=regime_score, confidence=float(np.clip(confidence, 0, 100)),
                weight=0.9,
                reasoning=f"Regime: {regime}. ADX={adx:.1f}, vol_ratio={vol_ratio:.2f}, price vs EMA50={price_vs_ema50:.1f}%.",
                bullish_factors=bullish_factors, bearish_factors=bearish_factors,
                supporting_data={"adx": adx, "vol_ratio": vol_ratio, "regime": regime,
                                  "price_vs_ema50": price_vs_ema50, "regime_score": regime_score},
                llm_ready_summary={"agent": self.agent_name, "signal": signal.value,
                                    "finding": f"Regime={regime}; ADX={adx:.1f}; regime_score={regime_score:.0f}; vol_ratio={vol_ratio:.2f}"},
                data_freshness=datetime.utcnow().isoformat(),
                execution_time_ms=int((time.time() - start) * 1000),
            )
        except Exception as e:
            logger.error(f"Agent01 failed for {symbol}: {e}")
            return self._degraded(start, str(e))

    def _degraded(self, start, err):
        return AgentOutput(agent_id=self.agent_id, agent_name=self.agent_name,
            signal=Signal.NEUTRAL, score=50.0, confidence=0.0, weight=0.9,
            reasoning="", bullish_factors=[], bearish_factors=[],
            supporting_data={}, llm_ready_summary={"agent": self.agent_name, "signal": "Neutral", "finding": "Failed"},
            data_freshness="", execution_time_ms=int((time.time() - start) * 1000), error=err)
