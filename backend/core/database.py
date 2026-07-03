"""
File path: backend/core/database.py
Purpose: SQLAlchemy engine, session factory, and declarative Base.
         All ORM models inherit from Base defined here.
         Provides get_db() dependency and init_db() startup function.

SPEC Reference: Section 10.1 (Database Architecture — SQLite MVP)
BUILD_PLAN Reference: Phase 1.3
"""

import logging
import os
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from config import settings

logger = logging.getLogger("app")


# ── Declarative Base ──────────────────────────────────────────────────────────

class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""
    pass


# ── Engine ────────────────────────────────────────────────────────────────────

def _make_engine():
    url = settings.DATABASE_URL
    is_sqlite = url.startswith("sqlite")

    connect_args = {}
    if is_sqlite:
        # SQLite: allow cross-thread usage (FastAPI uses thread pool)
        connect_args["check_same_thread"] = False

    engine = create_engine(
        url,
        connect_args=connect_args,
        # For SQLite: single connection pool (file-based)
        # For PostgreSQL: use pool_size=10, max_overflow=20
        pool_pre_ping=True,  # Detect stale connections
        echo=settings.DEBUG,  # Log SQL statements in DEBUG mode
    )

    # Enable WAL mode for SQLite — much better concurrent read performance
    if is_sqlite:
        @event.listens_for(engine, "connect")
        def set_sqlite_pragmas(dbapi_connection, _):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA synchronous=NORMAL")
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.execute("PRAGMA cache_size=-64000")   # 64MB cache
            cursor.execute("PRAGMA temp_store=MEMORY")
            cursor.close()

    logger.info(f"Database engine created: {url.split('///')[0]}///***")
    return engine


engine = _make_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# ── Dependency ────────────────────────────────────────────────────────────────

def get_db():
    """
    FastAPI dependency — yields a SQLAlchemy session per request.
    Auto-commits on success, rolls back on exception, always closes.

    Usage:
        @router.get("/example")
        def example(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


# ── Startup ───────────────────────────────────────────────────────────────────

def init_db() -> None:
    """
    Create all tables defined in ORM models if they don't exist.
    Called from main.py lifespan startup event AFTER alembic migrations run.
    In production: rely entirely on Alembic — this is a safety net for dev.
    """
    # Ensure data directory exists
    db_url = settings.DATABASE_URL
    if db_url.startswith("sqlite:///"):
        db_path = db_url.replace("sqlite:///", "")
        os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)

    # Import all models to register them with Base.metadata
    # (models must be imported before create_all — order follows FK deps)
    from modules.auth.models import User, UserSession                          # noqa: F401
    from modules.market_data.models import Symbol, CommodityData               # noqa: F401
    from modules.agents.models import AgentDefinition, AgentRun                # noqa: F401
    from modules.agents.models import AgentOutput as AgentOutputModel          # noqa: F401
    from modules.predictions.models import (                                   # noqa: F401
        Prediction, PredictionReason, PredictionContributor
    )
    from modules.explainability.models import PredictionExplanation            # noqa: F401
    from modules.news.models import NewsArticle, NewsSentiment                 # noqa: F401
    from modules.institutional.models import (                                 # noqa: F401
        InstitutionalFlow, DarkPoolActivity, InsiderTransaction, ThirteenFHolding
    )
    from modules.options.models import OptionsSnapshot, VIXData                # noqa: F401
    from modules.signals.models import TradeSignal                             # noqa: F401
    from modules.backtesting.models import Backtest, BacktestResult            # noqa: F401
    from modules.alerts.models import Alert                                    # noqa: F401
    from modules.monitoring.models import (                                    # noqa: F401
        SystemMetrics, APIHealth, DataSourceHealth, AgentHealth, AuditLog
    )
    from modules.performance.models import PredictionPerformance               # noqa: F401
    from modules.admin.models import SystemSetting                             # noqa: F401

    Base.metadata.create_all(bind=engine)
    logger.info("Database tables verified / created")


def check_db_health() -> dict:
    """
    Run a lightweight DB connectivity check.
    Returns {"status": "healthy"|"unhealthy", "latency_ms": int}
    """
    import time
    start = time.perf_counter()
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        latency_ms = int((time.perf_counter() - start) * 1000)
        return {"status": "healthy", "latency_ms": latency_ms}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
