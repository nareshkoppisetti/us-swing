"""Agent 10 — Macro News Impact | News & Macro | Tier 1 | depends: [7,11]"""
import time, logging, numpy as np
from datetime import datetime
from modules.agents.base_agent import BaseAgent, AgentOutput, Signal
logger = logging.getLogger("agents")
BULL_THEMES = {"rate cut":15,"stimulus":12,"dovish":10,"rally":8,"growth":6}
BEAR_THEMES = {"rate hike":-15,"hawkish":-12,"recession":-12,"inflation":-8,"default":-10,"crash":-15}

class Agent10(BaseAgent):
    agent_id=10; agent_name="Macro News Impact"; category="News & Macro"
    refresh_frequency="30min"; dependencies=[7,11]; tier=1

    def run(self, symbol, context):
        start = time.time()
        try:
            a7 = context.get(7); a11 = context.get(11)
            headline = ""
            if a7 and not a7.error: headline = str(a7.supporting_data.get("top_headline","")).lower()
            macro_score = (a11.score if a11 and not a11.error else 50) / 100.0

            impact = 0; dominant_theme = "Neutral"; theme_dir = "neutral"
            for theme, val in {**BULL_THEMES, **BEAR_THEMES}.items():
                if theme in headline:
                    impact += val
                    if abs(val) > abs(impact - val): dominant_theme = theme; theme_dir = "bullish" if val>0 else "bearish"

            impact = float(np.clip(impact, -50, 50))
            score = 50 + impact + (macro_score - 0.5) * 10
            score = float(np.clip(score, 0, 100))
            signal = Signal.BULLISH if score >= 58 else (Signal.BEARISH if score <= 42 else Signal.NEUTRAL)

            return AgentOutput(agent_id=self.agent_id,agent_name=self.agent_name,
                signal=signal,score=score,confidence=float(np.clip(35+abs(impact)*0.6,0,75)),
                weight=0.65,reasoning=f"Macro news impact={impact:.0f}; theme={dominant_theme}",
                bullish_factors=[f"Macro theme: {dominant_theme}"] if theme_dir=="bullish" else [],
                bearish_factors=[f"Macro theme: {dominant_theme}"] if theme_dir=="bearish" else [],
                supporting_data={"macro_news_impact":impact,"dominant_theme":dominant_theme,"theme_direction":theme_dir},
                llm_ready_summary={"agent":self.agent_name,"signal":signal.value,
                    "finding":f"Impact={impact:.0f}; theme={dominant_theme}; direction={theme_dir}"},
                data_freshness=datetime.utcnow().isoformat(),execution_time_ms=int((time.time()-start)*1000))
        except Exception as e:
            return AgentOutput(agent_id=self.agent_id,agent_name=self.agent_name,signal=Signal.NEUTRAL,
                score=50.0,confidence=0.0,weight=0.65,reasoning="",bullish_factors=[],bearish_factors=[],
                supporting_data={},llm_ready_summary={"agent":self.agent_name,"signal":"Neutral","finding":"Failed"},
                data_freshness="",execution_time_ms=int((time.time()-start)*1000),error=str(e))
