"""Agent 04 — Market Momentum | Direction | Tier 1"""
import time, logging, numpy as np
from datetime import datetime
from modules.agents.base_agent import BaseAgent, AgentOutput, Signal
logger = logging.getLogger("agents")

class Agent04(BaseAgent):
    agent_id=4; agent_name="Market Momentum"; category="Direction"
    refresh_frequency="15min"; dependencies=[]; tier=1

    def run(self, symbol, context):
        start = time.time()
        try:
            from modules.market_data.service import MarketDataService
            svc = MarketDataService()
            df = svc.get_ohlcv(symbol, period="1y")
            if df is None or len(df) < 30: raise ValueError("Insufficient data")
            close = df["close"].astype(float)

            # RSI 14
            rsi = svc._compute_rsi(close, 14) or 50.0
            # MACD
            ema12 = close.ewm(span=12,adjust=False).mean()
            ema26 = close.ewm(span=26,adjust=False).mean()
            macd  = ema12 - ema26
            signal_line = macd.ewm(span=9,adjust=False).mean()
            macd_val  = float(macd.iloc[-1])
            sig_val   = float(signal_line.iloc[-1])
            macd_bull = macd_val > sig_val
            # ROC
            roc10 = float((close.iloc[-1]/close.iloc[-11]-1)*100) if len(close)>11 else 0
            roc20 = float((close.iloc[-1]/close.iloc[-21]-1)*100) if len(close)>21 else 0
            # Stochastic
            lo14 = close.rolling(14).min()
            hi14 = close.rolling(14).max()
            stoch_k = float(((close - lo14)/(hi14 - lo14 + 1e-9)*100).iloc[-1])

            # Composite momentum score
            rsi_score  = 50 + (rsi - 50) * 0.6
            macd_score = 65 if macd_bull else 35
            roc_score  = 50 + np.clip(roc10 * 3, -30, 30)
            stoch_score= 50 + (stoch_k - 50) * 0.4
            momentum_score = (rsi_score*0.35 + macd_score*0.30 + roc_score*0.20 + stoch_score*0.15)
            momentum_score = float(np.clip(momentum_score, 0, 100))

            signal = Signal.BULLISH if momentum_score >= 60 else (Signal.BEARISH if momentum_score <= 40 else Signal.NEUTRAL)
            conf = 35 + abs(momentum_score - 50) * 0.9

            bf, brf = [], []
            if 40 <= rsi <= 70 and macd_bull: bf.append(f"RSI={rsi:.1f} (healthy range) + MACD bullish crossover")
            if roc10 > 2: bf.append(f"ROC-10d: +{roc10:.1f}% positive momentum")
            if rsi > 70: brf.append(f"RSI={rsi:.1f} — overbought territory")
            if rsi < 30: bf.append(f"RSI={rsi:.1f} — oversold, potential bounce")
            if not macd_bull: brf.append(f"MACD below signal line — bearish momentum")
            if roc10 < -2: brf.append(f"ROC-10d: {roc10:.1f}% — negative momentum")

            return AgentOutput(agent_id=self.agent_id,agent_name=self.agent_name,
                signal=signal,score=momentum_score,confidence=float(np.clip(conf,0,90)),
                weight=0.8,reasoning=f"RSI={rsi:.1f}, MACD_bull={macd_bull}, ROC10={roc10:.1f}%, Stoch={stoch_k:.1f}",
                bullish_factors=bf,bearish_factors=brf,
                supporting_data={"rsi_14":rsi,"macd":macd_val,"macd_signal":sig_val,"roc_10":roc10,"roc_20":roc20,"stoch_k":stoch_k},
                llm_ready_summary={"agent":self.agent_name,"signal":signal.value,
                    "finding":f"Momentum={momentum_score:.0f}; RSI={rsi:.1f}; MACD_bull={macd_bull}; ROC10={roc10:.1f}%"},
                data_freshness=datetime.utcnow().isoformat(),execution_time_ms=int((time.time()-start)*1000))
        except Exception as e:
            logger.error(f"Agent04 failed: {e}")
            return AgentOutput(agent_id=self.agent_id,agent_name=self.agent_name,signal=Signal.NEUTRAL,
                score=50.0,confidence=0.0,weight=0.8,reasoning="",bullish_factors=[],bearish_factors=[],
                supporting_data={},llm_ready_summary={"agent":self.agent_name,"signal":"Neutral","finding":"Failed"},
                data_freshness="",execution_time_ms=int((time.time()-start)*1000),error=str(e))
