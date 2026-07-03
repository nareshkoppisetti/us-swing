"""
File path: backend/core/logging.py
Purpose: Structured JSON logging configuration for the platform.
         Sets up four log files with rotating handlers.
         Called once from main.py via setup_logging().

SPEC Reference: Section 18.1 (Logging Strategy)
BUILD_PLAN Reference: Phase 1.6

Log files:
  logs/app.log         — general application events (INFO+)
  logs/agents.log      — agent execution events (INFO+)
  logs/predictions.log — prediction generation events (INFO+)
  logs/errors.log      — all errors and exceptions (ERROR+)
"""

import logging
import logging.handlers
import os
import sys
from pythonjsonlogger import jsonlogger


def setup_logging(log_dir: str | None = None, debug: bool | None = None) -> None:
    """
    Configure all loggers. Call once at app startup from main.py.

    Args:
        log_dir: Directory for log files. Defaults to settings.LOG_DIR.
        debug:   Enable DEBUG level. Defaults to settings.DEBUG.
    """
    from config import settings

    log_dir = log_dir or settings.LOG_DIR
    debug = debug if debug is not None else settings.DEBUG

    os.makedirs(log_dir, exist_ok=True)

    root_level = logging.DEBUG if debug else logging.INFO

    # ── JSON formatter ────────────────────────────────────────────────────────
    json_fmt = jsonlogger.JsonFormatter(
        fmt="%(asctime)s %(levelname)s %(name)s %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
        rename_fields={"asctime": "timestamp", "levelname": "level", "name": "logger"},
    )

    # ── Console formatter (human-readable) ────────────────────────────────────
    console_fmt = logging.Formatter(
        fmt="%(asctime)s [%(levelname)-8s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )

    def _rotating(filename: str, level: int) -> logging.Handler:
        h = logging.handlers.RotatingFileHandler(
            os.path.join(log_dir, filename),
            maxBytes=10 * 1024 * 1024,  # 10 MB per file
            backupCount=5,
            encoding="utf-8",
        )
        h.setLevel(level)
        h.setFormatter(json_fmt)
        return h

    # ── Root logger ───────────────────────────────────────────────────────────
    root = logging.getLogger()
    root.setLevel(root_level)
    root.handlers.clear()

    # Console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(root_level)
    console_handler.setFormatter(console_fmt)
    root.addHandler(console_handler)

    # app.log — all INFO+
    root.addHandler(_rotating("app.log", logging.INFO))

    # errors.log — ERROR+ from ALL loggers
    root.addHandler(_rotating("errors.log", logging.ERROR))

    # ── Dedicated loggers ─────────────────────────────────────────────────────

    # agents.log
    agents_log = logging.getLogger("agents")
    agents_log.addHandler(_rotating("agents.log", logging.INFO))
    agents_log.propagate = True   # also appear in app.log + console

    # predictions.log
    predictions_log = logging.getLogger("predictions")
    predictions_log.addHandler(_rotating("predictions.log", logging.INFO))
    predictions_log.propagate = True

    # ── Silence noisy third-party loggers ─────────────────────────────────────
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING if not debug else logging.INFO)
    logging.getLogger("apscheduler").setLevel(logging.WARNING)
    logging.getLogger("yfinance").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)

    logging.getLogger("app").info(
        "Logging configured",
        extra={"log_dir": log_dir, "level": "DEBUG" if debug else "INFO"},
    )
