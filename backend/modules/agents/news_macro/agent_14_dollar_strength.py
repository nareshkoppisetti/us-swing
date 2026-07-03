"""Agent 14 — Dollar Strength | News & Macro | Tier 1
Measures USD strength via DXY (DX-Y.NYB) or UUP ETF proxy.
Strong USD = bearish for equities/commodities.
Per SPEC BUILD_PLAN Phase 5.

Output supporting_data fields:
  dxy_price, dxy_sma20, dxy_sma50, dxy_roc20, dxy_rsi,
  dollar_strength_score, equity_impact_score,
  dxy_trend (Rising/Falling/Neutral), above_ema200
"""
import time
import logging
import numpy as np
from datetime import datetime
from modules.agents.base_agent import BaseAgent, AgentOutput, Signal

logger = logging.getLogger("agents")


class Agent14(BaseAgent):
    agent_id = 14
    agent_name = "Dollar Strength"
    category = "News & Macro"
    refresh_frequency = "daily"
    dependencies = []
    tier = 1

    def run(self, symbol, context):
        start = time.time()
        try:
            from modules.market_data.service import MarketDataService
            svc = MarketDataService()

            # Try DXY futures first, fall back to UUP ETF
            dxy_df = svc.get_ohlcv("DX-Y.NYB", period="6mo")
            if dxy_df is None or len(dxy_df) < 20:
                dxy_df = svc.get_ohlcv("UUP", period="6mo")
            if dxy_df is None or len(dxy_df) < 20:
                raise ValueError("No DXY/UUP data available")

            close = dxy_df["close"].astype(float)
            price = float(close.iloc[-1])
            n = len(close)

            # Moving averages
            sma20 = float(close.rolling(20).mean().iloc[-1])
            sma50 = float(close.rolling(50).mean().iloc[-1]) if n >= 50 else sma20
            ema200 = float(close.ewm(span=200).mean().iloc[-1]) if n >= 60 else sma50

            # Rate of change
            roc20 = ((price / float(close.iloc[-21])) - 1) * 100 if n >= 21 else 0.0

            # RSI-14
            delta = close.diff()
            gain = delta.clip(lower=0).rolling(14).mean()
            loss = (-delta.clip(upper=0)).rolling(14).mean()
            rs = gain / loss.replace(0, np.nan)
            rsi_series = 100 - (100 / (1 + rs))
            dxy_rsi = float(rsi_series.iloc[-1]) if not np.isnan(rsi_series.iloc[-1]) else 50.0

            # Trend classification
            if price > sma20 and roc20 > 0.5:
                dxy_trend = "Rising"
            elif price < sma20 and roc20 < -0.5:
                dxy_trend = "Falling"
            else:
                dxy_trend = "Neutral"

            above_sma20 = price > sma20
            above_sma50 = price > sma50
            above_ema200 = price > ema200

            # Dollar strength score 0-100 (higher = stronger USD)
            strength_score = 50.0
            if above_sma20:   strength_score += 12
            if above_sma50:   strength_score += 8
            if above_ema200:  strength_score += 10
            strength_score += np.clip(roc20 * 3, -15, 15)
            if dxy_rsi > 60:  strength_score += 5
            if dxy_rsi < 40:  strength_score -= 5
            strength_score = float(np.clip(strength_score, 0, 100))

            # Equity impact = inverse (strong USD = headwind for equities)
            equity_impact = 100.0 - strength_score

            # Signal is from equity perspective: bullish = weak USD = good for stocks
            signal = (Signal.BULLISH if equity_impact >= 58
                      else Signal.BEARISH if equity_impact <= 42
                      else Signal.NEUTRAL)

            bullish_factors = []
            bearish_factors = []
            if equity_impact > 55:
                bullish_factors.append(f"Weak USD ({dxy_trend}) — favorable for international earnings")
            if equity_impact < 45:
                bearish_factors.append(f"Strong USD ({dxy_trend}) — headwind for large-cap revenue")
            if abs(roc20) > 3:
                bearish_factors.append(f"DXY 20d ROC: {roc20:+.1f}% — significant dollar move")

            return AgentOutput(
                agent_id=self.agent_id,
                agent_name=self.agent_name,
                signal=signal,
                score=equity_impact,
                confidence=float(np.clip(35 + abs(equity_impact - 50) * 0.5, 0, 80)),
                weight=0.7,
                reasoning=(
                    f"DXY={price:.2f}, SMA20={sma20:.2f}, ROC20={roc20:+.1f}%, "
                    f"RSI={dxy_rsi:.0f}, trend={dxy_trend}"
                ),
                bullish_factors=bullish_factors,
                bearish_factors=bearish_factors,
                supporting_data={
                    "dxy_price": round(price, 4),
                    "dxy_sma20": round(sma20, 4),
                    "dxy_sma50": round(sma50, 4),
                    "dxy_roc20": round(roc20, 2),
                    "dxy_rsi":   round(dxy_rsi, 1),
                    "dxy_trend": dxy_trend,
                    "above_ema200": above_ema200,
                    "dollar_strength_score": round(strength_score, 1),
                    "equity_impact_score":   round(equity_impact, 1),
                },
                llm_ready_summary={
                    "agent": self.agent_name,
                    "signal": signal.value,
                    "finding": (
                        f"DXY={price:.2f}; trend={dxy_trend}; RSI={dxy_rsi:.0f}; "
                        f"ROC20={roc20:+.1f}%; equity_impact={equity_impact:.0f}"
                    ),
                },
                data_freshness=datetime.utcnow().isoformat(),
                execution_time_ms=int((time.time() - start) * 1000),
            )

        except Exception as e:
            logger.error(f"Agent14 failed: {e}")
            return AgentOutput(
                agent_id=self.agent_id, agent_name=self.agent_name,
                signal=Signal.NEUTRAL, score=50.0, confidence=0.0, weight=0.7,
                reasoning="", bullish_factors=[], bearish_factors=[],
                supporting_data={},
                llm_ready_summary={"agent": self.agent_name, "signal": "Neutral", "finding": "Failed"},
                data_freshness="",
                execution_time_ms=int((time.time() - start) * 1000),
                error=str(e),
            )
