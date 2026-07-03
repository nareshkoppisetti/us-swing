"""
File path: backend/main.py
Purpose: FastAPI application entry point.
         Initializes all subsystems and registers all routers.

SPEC Reference: Section 9.1 (Backend Architecture)
BUILD_PLAN Reference: Phase 1.12
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from core.logging import setup_logging
from core.database import init_db
from core.cache import init_cache
from core.middleware import setup_middleware
from core.websocket import websocket_endpoint, ws_manager

# ── Import all routers ────────────────────────────────────────────────────────
from modules.auth.router              import router as auth_router
from modules.market_data.router       import router as market_router
from modules.agents.router            import router as agents_router
from modules.predictions.router       import router as predictions_router
from modules.explainability.router    import router as explanations_router
from modules.news.router              import router as news_router
from modules.institutional.router     import router as institutional_router
from modules.options.router           import router as options_router
from modules.signals.router           import router as signals_router
from modules.backtesting.router       import router as backtesting_router
from modules.performance.router       import router as performance_router
from modules.alerts.router            import router as alerts_router
from modules.symbol_search.router     import router as symbols_router
from modules.monitoring.router        import router as monitoring_router
from modules.admin.router             import router as admin_router

logger = logging.getLogger("app")

PREFIX = "/api/v1"


# ── Lifespan ──────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown lifecycle handler."""
    # ── STARTUP ──────────────────────────────────────────────────────────────
    setup_logging()
    logger.info("USA Swing platform starting up...")

    # Initialize cache (must happen before middleware which uses it)
    cache = init_cache()
    app.state.cache = cache

    # Initialize database tables (safety net; Alembic handles migrations)
    init_db()

    # Load symbol registry into memory
    try:
        from modules.symbol_search import symbol_registry
        symbol_registry.load()
    except Exception as e:
        logger.warning(f"Symbol registry load failed (non-fatal): {e}")

    # Start agent scheduler
    try:
        from modules.agents.scheduler import start_scheduler
        start_scheduler()
        logger.info("Agent scheduler started")
    except Exception as e:
        logger.warning(f"Agent scheduler start failed (non-fatal): {e}")

    logger.info(
        "Startup complete",
        extra={
            "env": settings.APP_ENV,
            "debug": settings.DEBUG,
            "db": settings.DATABASE_URL.split("///")[0],
        },
    )

    yield

    # ── SHUTDOWN ──────────────────────────────────────────────────────────────
    logger.info("USA Swing platform shutting down...")
    try:
        from modules.agents.scheduler import stop_scheduler
        stop_scheduler()
    except Exception:
        pass
    if cache:
        cache.close()


# ── App ───────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="USA Swing — Market Intelligence API",
    description="Institutional-grade swing trading prediction platform. 42-agent pipeline.",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    openapi_url="/openapi.json" if settings.DEBUG else None,
    lifespan=lifespan,
)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Custom middleware and exception handlers ───────────────────────────────────
# Note: cache not available yet at module load — passed after startup via app.state
setup_middleware(app)


# ── Health check (unauthenticated) ────────────────────────────────────────────

@app.get("/health", tags=["Health"])
def health_check():
    """
    Platform health check. Returns 200 when the server is running.
    Used by load balancers and monitoring tools.
    """
    from core.database import check_db_health
    db_health = check_db_health()
    return {
        "status": "healthy" if db_health["status"] == "healthy" else "degraded",
        "version": "1.0.0",
        "env": settings.APP_ENV,
        "database": db_health,
        "websocket_connections": ws_manager.connection_count,
    }


# ── WebSocket ─────────────────────────────────────────────────────────────────

app.add_api_websocket_route("/ws", websocket_endpoint)


# ── API Routers ───────────────────────────────────────────────────────────────

app.include_router(auth_router,          prefix=f"{PREFIX}/auth")
app.include_router(market_router,        prefix=f"{PREFIX}/market")
app.include_router(agents_router,        prefix=f"{PREFIX}/agents")
app.include_router(predictions_router,   prefix=f"{PREFIX}/predictions")
app.include_router(explanations_router,  prefix=f"{PREFIX}/explanations")
app.include_router(news_router,          prefix=f"{PREFIX}/news")
app.include_router(institutional_router, prefix=f"{PREFIX}/institutional")
app.include_router(options_router,       prefix=f"{PREFIX}/options")
app.include_router(signals_router,       prefix=f"{PREFIX}/signals")
app.include_router(backtesting_router,   prefix=f"{PREFIX}/backtesting")
app.include_router(performance_router,   prefix=f"{PREFIX}/performance")
app.include_router(alerts_router,        prefix=f"{PREFIX}/alerts")
app.include_router(symbols_router,       prefix=f"{PREFIX}/symbols")
app.include_router(monitoring_router,    prefix=f"{PREFIX}/monitoring")
app.include_router(admin_router,         prefix=f"{PREFIX}/admin")
