"""Agent 15 — Sector Rotation | Institutional | Tier 1 | depends: [3,20]"""
import time, logging, numpy as np
from datetime import datetime
from modules.agents.base_agent import BaseAgent, AgentOutput, Signal
logger = logging.getLogger("agents")
SECTORS = {"XLK":"Tech","XLF":"Financials","XLE":"Energy","XLV":"Healthcare",
           "XLI":"Industrials","XLY":"Discretionary","XLP":"Staples","XLRE":"Real Estate"}

class Agent15(BaseAgent):
    agent_id=15; agent_name="Sector Rotation"; category="Institutional"
    refresh_frequency="daily"; dependencies=[3,20]; tier=1

    def run(self, symbol, context):
        start = time.time()
        try:
            from modules.market_data.service import MarketDataService
            svc = MarketDataService()
            perf = {}
            for etf, name in SECTORS.items():
                try:
                    df = svc.get_ohlcv(etf, period="3mo")
                    if df is None or len(df)<20: continue
                    close = df["close"].astype(float)
                    ret_1m = (close.iloc[-1]/close.iloc[-21]-1)*100 if len(close)>21 else 0
                    ret_3m = (close.iloc[-1]/close.iloc[0]-1)*100
                    rsi    = svc._compute_rsi(close, 14) or 50
                    perf[etf] = {"name":name,"ret_1m":ret_1m,"ret_3m":ret_3m,"rsi":rsi}
                except Exception: pass

            if not perf: raise ValueError("No sector data")

            # Find leader/laggard by 1-month return
            sorted_sectors = sorted(perf.items(), key=lambda x: x[1]["ret_1m"], reverse=True)
            leader = sorted_sectors[0] if sorted_sectors else None
            laggard = sorted_sectors[-1] if sorted_sectors else None

            # Is symbol's sector leading?
            quote = svc.get_quote(symbol)
            sym_sector = (quote.get("sector") or "").replace(" ","")
            sector_match = any(s["name"].lower() in sym_sector.lower() for _,s in sorted_sectors[:3])

            avg_1m = float(np.mean([v["ret_1m"] for v in perf.values()]))
            score = 50 + avg_1m * 2
            score = float(np.clip(score, 0, 100))
            signal = Signal.BULLISH if score >= 58 else (Signal.BEARISH if score <= 42 else Signal.NEUTRAL)

            bf  = [f"Sector leader: {leader[1]['name']} +{leader[1]['ret_1m']:.1f}% (1m)"] if leader else []
            brf = [f"Sector laggard: {laggard[1]['name']} {laggard[1]['ret_1m']:.1f}% (1m)"] if laggard else []
            if sector_match: bf.append("Symbol's sector is among top 3 performers")

            return AgentOutput(agent_id=self.agent_id,agent_name=self.agent_name,
                signal=signal,score=score,confidence=float(np.clip(40+abs(avg_1m)*2,0,85)),
                weight=0.75,reasoning=f"Avg sector 1m return={avg_1m:.1f}%; leader={leader[1]['name'] if leader else 'N/A'}",
                bullish_factors=bf,bearish_factors=brf,
                supporting_data={"avg_sector_1m_return":avg_1m,"leader":leader[1] if leader else {},"laggard":laggard[1] if laggard else {}},
                llm_ready_summary={"agent":self.agent_name,"signal":signal.value,
                    "finding":f"Avg sector 1m={avg_1m:.1f}%; leader={leader[1]['name'] if leader else 'N/A'}"},
                data_freshness=datetime.utcnow().isoformat(),execution_time_ms=int((time.time()-start)*1000))
        except Exception as e:
            return AgentOutput(agent_id=self.agent_id,agent_name=self.agent_name,signal=Signal.NEUTRAL,
                score=50.0,confidence=0.0,weight=0.75,reasoning="",bullish_factors=[],bearish_factors=[],
                supporting_data={},llm_ready_summary={"agent":self.agent_name,"signal":"Neutral","finding":"Failed"},
                data_freshness="",execution_time_ms=int((time.time()-start)*1000),error=str(e))
