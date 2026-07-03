"""Agent 09 — Event Detection | News & Macro | Tier 1 | depends: [7]
Scans Agent 7 news headlines AND the economic calendar for upcoming
high-impact events: CPI, PPI, GDP, FOMC, NFP, PCE.
Per SPEC BUILD_PLAN Phase 5.
"""
import time
import logging
import numpy as np
from datetime import datetime, date, timedelta
from modules.agents.base_agent import BaseAgent, AgentOutput, Signal

logger = logging.getLogger("agents")

HIGH_IMPACT_KEYWORDS = [
    "CPI", "PPI", "GDP", "FOMC", "NFP", "Non-Farm",
    "Federal Reserve", "rate decision", "inflation", "unemployment",
    "PCE", "Payroll", "payrolls", "Jackson Hole",
]


class Agent09(BaseAgent):
    agent_id = 9
    agent_name = "Event Detection"
    category = "News & Macro"
    refresh_frequency = "30min"
    dependencies = [7]
    tier = 1

    def run(self, symbol, context):
        start = time.time()
        try:
            # ── Source 1: Economic Calendar ──────────────────────────────────
            from modules.news.economic_calendar import get_upcoming_events
            calendar_events = get_upcoming_events(days_ahead=7)

            nearest_cal_event = None
            min_days = 999
            for ev in calendar_events:
                if ev["days_until"] < min_days:
                    min_days = ev["days_until"]
                    nearest_cal_event = ev

            # ── Source 2: News headlines from Agent 7 ────────────────────────
            a7 = context.get(7)
            news_event_found = False
            news_event_name = None
            if a7 and not a7.error and a7.supporting_data:
                top_headline = str(a7.supporting_data.get("top_headline", ""))
                headline_upper = top_headline.upper()
                for kw in HIGH_IMPACT_KEYWORDS:
                    if kw.upper() in headline_upper:
                        news_event_found = True
                        news_event_name = kw
                        break

            # ── Determine dominant event ─────────────────────────────────────
            # Calendar is authoritative for scheduled events;
            # news headlines catch unscheduled announcements.
            if nearest_cal_event and nearest_cal_event["days_until"] <= 7:
                event_name = nearest_cal_event["name"]
                days_ahead = nearest_cal_event["days_until"]
                is_high_impact = nearest_cal_event["impact"] == "high"
            elif news_event_found:
                event_name = news_event_name
                days_ahead = 1   # assume imminent if in headlines
                is_high_impact = True
            else:
                event_name = "None"
                days_ahead = 999
                is_high_impact = False

            # ── Risk scoring ─────────────────────────────────────────────────
            if days_ahead <= 1:
                risk = 90 if is_high_impact else 60
            elif days_ahead <= 2:
                risk = 75 if is_high_impact else 45
            elif days_ahead <= 3:
                risk = 65 if is_high_impact else 35
            elif days_ahead <= 7:
                risk = 40 if is_high_impact else 20
            else:
                risk = 5

            score = float(np.clip(50.0 - risk * 0.3, 0, 100))
            confidence = float(np.clip(55 - risk * 0.2, 20, 75))
            signal = Signal.NEUTRAL  # event risk is direction-agnostic

            bearish_factors = []
            if event_name != "None":
                bearish_factors.append(
                    f"High-impact event: {event_name} in {days_ahead}d — elevated uncertainty"
                )

            # Collect all upcoming high-impact events for LLM context
            upcoming_high = [
                f"{e['name']} in {e['days_until']}d"
                for e in calendar_events
                if e["impact"] == "high"
            ][:3]

            return AgentOutput(
                agent_id=self.agent_id,
                agent_name=self.agent_name,
                signal=signal,
                score=score,
                confidence=confidence,
                weight=0.65,
                reasoning=f"Event risk={risk}, event='{event_name}', days_ahead={days_ahead}",
                bullish_factors=[],
                bearish_factors=bearish_factors,
                supporting_data={
                    "event_risk_score": risk,
                    "next_event_name": event_name,
                    "days_ahead": days_ahead if days_ahead < 999 else None,
                    "is_high_impact": is_high_impact,
                    "upcoming_events": upcoming_high,
                },
                llm_ready_summary={
                    "agent": self.agent_name,
                    "signal": signal.value,
                    "finding": (
                        f"Next event: '{event_name}' in {days_ahead}d "
                        f"(risk={risk}); upcoming: {', '.join(upcoming_high) or 'none'}"
                    ),
                },
                data_freshness=datetime.utcnow().isoformat(),
                execution_time_ms=int((time.time() - start) * 1000),
            )

        except Exception as e:
            logger.error(f"Agent09 failed: {e}")
            return AgentOutput(
                agent_id=self.agent_id, agent_name=self.agent_name,
                signal=Signal.NEUTRAL, score=50.0, confidence=0.0,
                weight=0.65, reasoning="", bullish_factors=[], bearish_factors=[],
                supporting_data={},
                llm_ready_summary={"agent": self.agent_name, "signal": "Neutral", "finding": "Failed"},
                data_freshness="", execution_time_ms=int((time.time() - start) * 1000),
                error=str(e),
            )
