"""
File: backend/modules/agents/scheduler.py
Purpose: APScheduler-based scheduler for periodic agent re-runs.
         Per SPEC: 15min agents refresh every 15min, daily every night at 01:00 UTC.
"""
import logging
from datetime import datetime
from typing import List

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from modules.agents.engine import AgentEngine
from modules.symbol_search.symbol_registry import load as load_symbols

logger = logging.getLogger("agents")

_scheduler: BackgroundScheduler = None
WATCHLIST_SYMBOLS = ["SPY", "QQQ", "AAPL", "TSLA", "NVDA", "MSFT", "AMZN", "GOOGL"]


def _run_agents_for_symbols(symbols: List[str], label: str):
    """Run all agents for a list of symbols and log results."""
    engine = AgentEngine(db=None)
    for symbol in symbols:
        try:
            logger.info(f"[{label}] Scheduled run starting for {symbol}")
            results = engine.run_all(symbol)
            a33 = results.get(33)
            if a33 and not a33.error:
                logger.info(
                    f"[{label}] {symbol}: signal={a33.signal.value}, "
                    f"score={a33.score:.1f}, conf={a33.confidence:.1f}%"
                )
        except Exception as e:
            logger.error(f"[{label}] Scheduled run failed for {symbol}: {e}")


def _run_15min_agents():
    _run_agents_for_symbols(WATCHLIST_SYMBOLS, "15min")


def _run_hourly_agents():
    _run_agents_for_symbols(WATCHLIST_SYMBOLS, "hourly")


def _run_daily_agents():
    _run_agents_for_symbols(WATCHLIST_SYMBOLS, "daily")


def start_scheduler():
    """Start the APScheduler background scheduler."""
    global _scheduler
    if _scheduler and _scheduler.running:
        logger.warning("Scheduler already running")
        return

    _scheduler = BackgroundScheduler(timezone="UTC", daemon=True)

    # 15-minute refresh — market hours aware
    _scheduler.add_job(
        _run_15min_agents,
        trigger=IntervalTrigger(minutes=15),
        id="agents_15min",
        name="15-minute agent refresh",
        replace_existing=True,
        max_instances=1,
        misfire_grace_time=60,
    )

    # Hourly refresh
    _scheduler.add_job(
        _run_hourly_agents,
        trigger=IntervalTrigger(hours=1),
        id="agents_hourly",
        name="Hourly agent refresh",
        replace_existing=True,
        max_instances=1,
        misfire_grace_time=120,
    )

    # Daily at 01:00 UTC — macro/fundamental agents
    _scheduler.add_job(
        _run_daily_agents,
        trigger=CronTrigger(hour=1, minute=0),
        id="agents_daily",
        name="Daily agent refresh",
        replace_existing=True,
        max_instances=1,
    )

    _scheduler.start()
    logger.info("Agent scheduler started (15min / hourly / daily jobs)")


def stop_scheduler():
    global _scheduler
    if _scheduler and _scheduler.running:
        _scheduler.shutdown(wait=False)
        logger.info("Agent scheduler stopped")


def get_scheduler_status() -> dict:
    if _scheduler is None or not _scheduler.running:
        return {"running": False, "jobs": []}
    jobs = []
    for job in _scheduler.get_jobs():
        jobs.append({
            "id": job.id,
            "name": job.name,
            "next_run": str(job.next_run_time),
        })
    return {"running": True, "jobs": jobs}


def trigger_job(job_id: str) -> dict:
    """
    Manually run a scheduled job's function immediately, in addition to (not
    instead of) its normal schedule. Used by the Admin module.
    Raises ValueError if the job_id doesn't exist or the scheduler isn't running.
    """
    if _scheduler is None or not _scheduler.running:
        raise ValueError("Scheduler is not running")
    job = _scheduler.get_job(job_id)
    if job is None:
        raise ValueError(f"No scheduled job with id '{job_id}'")
    # Run the job's callable directly in a background thread so the API
    # request returns immediately rather than blocking on a full agent run.
    import threading
    threading.Thread(target=job.func, daemon=True).start()
    return {"job_id": job_id, "name": job.name, "triggered_at": __import__("datetime").datetime.utcnow().isoformat()}
