"""Agent 20 — ETF Flow Intelligence | Institutional | Tier 1"""
import time, logging, numpy as np
from datetime import datetime
from modules.agents.base_agent import BaseAgent, AgentOutput, Signal
logger = logging.getLogger("agents")
RELATED_ETFS = {"XLK":["AAPL","MSFT","NVDA","META","GOOGL"],"XLF":["JPM","BAC","GS","MS"],
                "XLE":["XOM","CVX","SLB"],"XLV":["UNH","JNJ","PFE"],"XLI":["GE","HON","MMM"]}

class Agent20(BaseAgent):
    agent_id=20; agent_name="ETF Flow Intelligence"; category="Institutional"
    refresh_frequency="daily"; dependencies=[]; tier=1

    def run(self, symbol, context):
        start = time.time()
        try:
            from modules.market_data.service import MarketDataService
            svc = MarketDataService()
            # Find sector ETF for this symbol
            sector_etf = next((etf for etf, symbols in RELATED_ETFS.items() if symbol in symbols), None)
            etfs_to_check = [sector_etf] if sector_etf else list(RELATED_ETFS.keys())[:3]
            scores, bf, brf = [], [], []
            for etf in etfs_to_check:
                try:
                    df = svc.get_ohlcv(etf, period="1mo")
                    if df is None or len(df)<5: continue
                    vol   = df["volume"].astype(float)
                    close = df["close"].astype(float)
                    avg_vol = float(vol.rolling(min(10,len(vol))).mean().iloc[-1])
                    today_vol = float(vol.iloc[-1])
                    vol_ratio = today_vol / avg_vol if avg_vol > 0 else 1.0
                    ret_5d = (float(close.iloc[-1]) / float(close.iloc[-6]) - 1)*100 if len(close)>5 else 0
                    etf_score = 50 + ret_5d*3 + (vol_ratio-1)*15
                    scores.append(etf_score)
                    if etf_score > 55: bf.append(f"{etf}: +{ret_5d:.1f}% 5d, vol={vol_ratio:.1f}x avg")
                    elif etf_score < 45: brf.append(f"{etf}: {ret_5d:.1f}% 5d, vol={vol_ratio:.1f}x avg")
                except Exception: pass

            score = float(np.clip(np.mean(scores) if scores else 50, 0, 100))
            signal = Signal.BULLISH if score >= 58 else (Signal.BEARISH if score <= 42 else Signal.NEUTRAL)

            return AgentOutput(agent_id=self.agent_id,agent_name=self.agent_name,
                signal=signal,score=score,confidence=float(np.clip(30+len(scores)*8,0,80)),
                weight=0.7,reasoning=f"ETF flow score={score:.1f} from {len(scores)} ETFs checked",
                bullish_factors=bf,bearish_factors=brf,
                supporting_data={"etf_scores_avg":score,"etfs_checked":len(scores),"sector_etf":sector_etf},
                llm_ready_summary={"agent":self.agent_name,"signal":signal.value,
                    "finding":f"ETF flow={score:.0f}; sector={sector_etf}; {len(scores)} ETFs"},
                data_freshness=datetime.utcnow().isoformat(),execution_time_ms=int((time.time()-start)*1000))
        except Exception as e:
            return AgentOutput(agent_id=self.agent_id,agent_name=self.agent_name,signal=Signal.NEUTRAL,
                score=50.0,confidence=0.0,weight=0.7,reasoning="",bullish_factors=[],bearish_factors=[],
                supporting_data={},llm_ready_summary={"agent":self.agent_name,"signal":"Neutral","finding":"Failed"},
                data_freshness="",execution_time_ms=int((time.time()-start)*1000),error=str(e))
