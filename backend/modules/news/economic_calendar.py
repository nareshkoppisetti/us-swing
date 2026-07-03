"""
File: backend/modules/news/economic_calendar.py
Purpose: Hardcoded + computed upcoming economic event calendar.
         Used by Agent 9 (Event Detection) and the news/economic-calendar endpoint.

Events covered: CPI, PPI, GDP, FOMC, NFP, PCE, Retail Sales, JOLTS, ISM.
Release schedule is approximate — monthly cadence computed from known anchor dates.
Per SPEC Section 9.2 (event calendar).
"""
import logging
from datetime import date, datetime, timedelta

logger = logging.getLogger("app")

# Anchor dates for 2025 known scheduled releases (approximate).
# These are extended forward each year by adding ~365 days per cycle.
_FOMC_MEETING_DATES_2025 = [
    "2025-01-29", "2025-03-19", "2025-05-07", "2025-06-18",
    "2025-07-30", "2025-09-17", "2025-10-29", "2025-12-10",
]
_FOMC_MEETING_DATES_2026 = [
    "2026-01-28", "2026-03-18", "2026-05-06", "2026-06-17",
    "2026-07-29", "2026-09-16", "2026-10-28", "2026-12-09",
]

def _generate_monthly_events(name: str, anchor_day: int, months_ahead: int = 3) -> list[dict]:
    """Generate monthly recurring event for next N months."""
    today = date.today()
    events = []
    for delta in range(months_ahead + 1):
        month = (today.month + delta - 1) % 12 + 1
        year = today.year + (today.month + delta - 1) // 12
        try:
            event_date = date(year, month, anchor_day)
            if event_date >= today:
                events.append({"name": name, "date": event_date.isoformat()})
        except ValueError:
            # anchor_day exceeds month length — use last day
            import calendar
            last_day = calendar.monthrange(year, month)[1]
            event_date = date(year, month, last_day)
            if event_date >= today:
                events.append({"name": name, "date": event_date.isoformat()})
    return events


def get_upcoming_events(days_ahead: int = 45) -> list[dict]:
    """
    Return list of upcoming economic events within the next N days.
    Each: { name, date, days_until, impact: "high"|"medium" }
    """
    today = date.today()
    cutoff = today + timedelta(days=days_ahead)

    raw_events = []

    # FOMC meeting dates
    for d_str in _FOMC_MEETING_DATES_2025 + _FOMC_MEETING_DATES_2026:
        raw_events.append({"name": "FOMC Meeting", "date": d_str})

    # Monthly reports (approximate release days of each month)
    raw_events += _generate_monthly_events("CPI Release", anchor_day=11)
    raw_events += _generate_monthly_events("PPI Release", anchor_day=14)
    raw_events += _generate_monthly_events("Non-Farm Payrolls (NFP)", anchor_day=4)  # first Friday ~4th
    raw_events += _generate_monthly_events("PCE Price Index", anchor_day=28)
    raw_events += _generate_monthly_events("Retail Sales", anchor_day=17)
    raw_events += _generate_monthly_events("JOLTS Job Openings", anchor_day=8)
    raw_events += _generate_monthly_events("ISM Manufacturing", anchor_day=2)
    raw_events += _generate_monthly_events("Initial Jobless Claims", anchor_day=17)

    # Quarterly GDP (approx last week of month after quarter end)
    for month_day in [("01", "30"), ("04", "30"), ("07", "30"), ("10", "30")]:
        for year in [today.year, today.year + 1]:
            raw_events.append({"name": "GDP Advance Estimate", "date": f"{year}-{month_day[0]}-{month_day[1]}"})

    # Filter to upcoming window and compute days_until
    events = []
    seen = set()
    for ev in raw_events:
        try:
            ev_date = date.fromisoformat(ev["date"])
        except (ValueError, TypeError):
            continue
        if ev_date < today or ev_date > cutoff:
            continue
        key = (ev["name"], ev_date.isoformat())
        if key in seen:
            continue
        seen.add(key)
        days_until = (ev_date - today).days
        events.append({
            "name": ev["name"],
            "date": ev_date.isoformat(),
            "days_until": days_until,
            "impact": "high" if any(k in ev["name"] for k in ["FOMC", "CPI", "NFP", "GDP"]) else "medium",
        })

    events.sort(key=lambda x: x["date"])
    return events


def get_next_high_impact_event() -> dict | None:
    """Return the nearest high-impact event."""
    events = get_upcoming_events(days_ahead=30)
    high = [e for e in events if e["impact"] == "high"]
    return high[0] if high else (events[0] if events else None)
