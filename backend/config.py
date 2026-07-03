"""
File path: backend/config.py
Purpose: Centralized platform configuration via Pydantic Settings.
         Reads from .env file and environment variables.
         Single source of truth for all config values.

SPEC Reference: Section 27.1 (Environment Configuration)
"""
from functools import lru_cache
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # --- Application ---
    APP_ENV: str = "development"          # development | production | test
    APP_SECRET_KEY: str                   # JWT signing key — min 32 chars — REQUIRED
    DEBUG: bool = True

    # --- Data APIs (all optional — agents degrade gracefully without them) ---
    ALPHA_VANTAGE_API_KEY: Optional[str] = None
    NEWS_API_KEY: Optional[str] = None
    FRED_API_KEY: Optional[str] = None
    NASDAQ_DATA_LINK_API_KEY: Optional[str] = None
    EIA_API_KEY: Optional[str] = None

    # --- LLM (xAI Grok — for explanation narratives) ---
    GROK_API_KEY: Optional[str] = None

    # --- Database ---
    DATABASE_URL: str = "sqlite:///./data/usa_swing.db"
    SCHEDULER_DB_URL: str = "sqlite:///./data/scheduler.db"

    # --- Cache (diskcache) ---
    CACHE_DIR: str = "./data/cache"
    CACHE_DEFAULT_TTL: int = 3600  # seconds

    # --- Storage ---
    PARQUET_DATA_DIR: str = "./data/market_data"
    FEATURES_DIR: str = "./data/features"
    MODELS_DIR: str = "./data/models"
    LOG_DIR: str = "./logs"

    # --- JWT (SPEC Section 17.2) ---
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # --- Platform ---
    SIGNAL_CONFIDENCE_THRESHOLD: float = 65.0
    MAX_FAILED_AGENTS_ALLOWED: int = 10

    # --- CORS ---
    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:3001"]

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
