"""
File path: backend/alembic/env.py
Purpose: Alembic migration environment. Imports all models so schema is auto-detected.

BUILD_PLAN Reference: Phase 1.1
"""
import sys
import os
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# Add backend to path so imports work
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Import Base + all models (order follows FK dependencies)
from core.database import Base                                                       # noqa: F401
from modules.auth.models import User, UserSession                                   # noqa: F401
from modules.market_data.models import Symbol, CommodityData                        # noqa: F401
from modules.agents.models import AgentDefinition, AgentRun                         # noqa: F401
from modules.agents.models import AgentOutput as AgentOutputModel                   # noqa: F401
from modules.predictions.models import Prediction, PredictionReason, PredictionContributor  # noqa: F401
from modules.explainability.models import PredictionExplanation                     # noqa: F401
from modules.news.models import NewsArticle, NewsSentiment                          # noqa: F401
from modules.institutional.models import (                                           # noqa: F401
    InstitutionalFlow, DarkPoolActivity, InsiderTransaction, ThirteenFHolding
)
from modules.options.models import OptionsSnapshot, VIXData                         # noqa: F401
from modules.signals.models import TradeSignal                                      # noqa: F401
from modules.backtesting.models import Backtest, BacktestResult                     # noqa: F401
from modules.alerts.models import Alert                                              # noqa: F401
from modules.monitoring.models import (                                              # noqa: F401
    SystemMetrics, APIHealth, DataSourceHealth, AgentHealth, AuditLog
)
from modules.performance.models import PredictionPerformance                        # noqa: F401

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_as_batch=True,   # Required for SQLite ALTER TABLE support
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_as_batch=True,   # Required for SQLite ALTER TABLE support
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
