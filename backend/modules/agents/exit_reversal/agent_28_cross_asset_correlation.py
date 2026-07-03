"""Agent 28 — Cross Asset Correlation | Exit & Reversal | Tier 1 | depends: [14,26]"""
import time, logging, numpy as np
from datetime import datetime
from modules.agents.base_agent import BaseAgent, AgentOutput, Signal
logger = logging.getLogger("agents")

class Agent28(BaseAgent):
    agent_id=28; agent_name="Cross Asset Correlation"; category="Exit & Reversal"
    refresh_frequency="daily"; dependencies=[14,26]; tier=1

    def run(self, symbol, context):
        start = time.time()
        try:
            from modules.market_data.service import MarketDataService
            svc = MarketDataService()
            df  = svc.get_ohlcv(symbol, period="6mo")
            spy = svc.get_ohlcv("SPY", period="6mo")
            if df is None or spy is None or len(df)<30: raise ValueError("Insufficient data")
            sym_ret = df["close"].astype(float).pct_change().dropna()
            spy_ret = spy["close"].astype(float).pct_change().dropna()
            min_len = min(len(sym_ret), len(spy_ret))
            spy_corr = float(np.corrcoef(sym_ret.values[-min_len:], spy_ret.values[-min_len:])[0,1])
            rolling_corr = float(np.corrcoef(sym_ret.values[-30:], spy_ret.values[-30:])[0,1]) if min_len>=30 else spy_corr

            score = 50 + (1 - spy_corr) * 25
            score = float(np.clip(score, 0, 100))
            signal = Signal.NEUTRAL if spy_corr > 0.7 else (Signal.BULLISH if rolling_corr < 0.5 else Signal.NEUTRAL)

            return AgentOutput(agent_id=self.agent_id,agent_name=self.agent_name,
                signal=signal,score=score,confidence=float(np.clip(35+abs(1-spy_corr)*30,0,80)),
                weight=0.7,reasoning=f"{symbol}/SPY corr={spy_corr:.2f} (6m); rolling 30d={rolling_corr:.2f}",
                bullish_factors=[f"Low SPY correlation ({spy_corr:.2f}) — good diversifier"] if spy_corr<0.5 else [],
                bearish_factors=[f"High SPY correlation ({spy_corr:.2f}) — moves with market"] if spy_corr>0.85 else [],
                supporting_data={"spy_correlation":spy_corr,"rolling_30d_corr":rolling_corr},
                llm_ready_summary={"agent":self.agent_name,"signal":signal.value,
                    "finding":f"SPY_corr={spy_corr:.2f}; rolling30d={rolling_corr:.2f}"},
                data_freshness=datetime.utcnow().isoformat(),execution_time_ms=int((time.time()-start)*1000))
        except Exception as e:
            return AgentOutput(agent_id=self.agent_id,agent_name=self.agent_name,signal=Signal.NEUTRAL,
                score=50.0,confidence=0.0,weight=0.7,reasoning="",bullish_factors=[],bearish_factors=[],
                supporting_data={},llm_ready_summary={"agent":self.agent_name,"signal":"Neutral","finding":"Failed"},
                data_freshness="",execution_time_ms=int((time.time()-start)*1000),error=str(e))
