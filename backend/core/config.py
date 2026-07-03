"""
File path: backend/core/config.py
Purpose: Centralized configuration management using Pydantic Settings.
         Reads from environment variables and .env file.
         Single source of truth for all configuration values.
         Per SPEC Section 10.1.

Usage:
    from core.config import settings
    api_key = settings.ALPHA_VANTAGE_API_KEY
"""
from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Platform configuration.
    All values can be overridden via environment variables or .env file.
    """

    # --- Application ---
    APP_ENV: str = Field(default="development", description="development | production | test")
    APP_SECRET_KEY: str = Field(default="CHANGE_ME_IN_PRODUCTION_32_CHARS_MIN")
    DEBUG: bool = Field(default=True)
    APP_HOST: str = Field(default="0.0.0.0")
    APP_PORT: int = Field(default=8000)

    # --- Data APIs ---
    ALPHA_VANTAGE_API_KEY: str = Field(default="", description="Alpha Vantage REST API key")
    NEWS_API_KEY: str = Field(default="", description="NewsAPI key")
    FRED_API_KEY: str = Field(default="", description="FRED (St. Louis Fed) API key")
    NASDAQ_DATA_LINK_API_KEY: str = Field(default="", description="Nasdaq Data Link (Quandl) key")
    EIA_API_KEY: str = Field(default="", description="EIA energy data API key")

    # --- LLM (xAI Grok) ---
    GROK_API_KEY: str = Field(default="", description="xAI Grok API key")

    # --- Database ---
    DATABASE_URL: str = Field(default="sqlite:///./data/usa_swing.db")
    SCHEDULER_DB_URL: str = Field(default="sqlite:///./data/scheduler.db")

    # --- Cache ---
    CACHE_DIR: str = Field(default="./data/cache")
    CACHE_DEFAULT_TTL: int = Field(default=3600, description="Cache TTL in seconds")

    # --- Storage ---
    PARQUET_DATA_DIR: str = Field(default="./data/market_data")
    FEATURES_DIR: str = Field(default="./data/features")
    MODELS_DIR: str = Field(default="./data/models")
    LOG_DIR: str = Field(default="./logs")

    # --- JWT ---
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=15)
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7)
    JWT_ALGORITHM: str = Field(default="HS256")

    # --- Email (optional alerts delivery) ---
    SMTP_HOST: str = Field(default="")
    SMTP_PORT: int = Field(default=587)
    SMTP_USER: str = Field(default="")
    SMTP_PASSWORD: str = Field(default="")
    SMTP_FROM_ADDRESS: str = Field(default="noreply@usa-swing.local")

    # --- Platform Settings ---
    SIGNAL_CONFIDENCE_THRESHOLD: float = Field(default=65.0)
    MAX_FAILED_AGENTS_ALLOWED: int = Field(default=10)
    DEFAULT_WATCH_SYMBOLS: list[str] = Field(
        default=["SPY", "QQQ", "AAPL", "MSFT", "NVDA", "AMZN", "TSLA", "GC=F", "CL=F"]
    )

    # --- CORS ---
    ALLOWED_ORIGINS: list[str] = Field(
        default=["http://localhost:3000", "http://localhost:3001"]
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Cached settings singleton. Import and use 'settings' instead of calling directly."""
    return Settings()


# Convenience singleton for import
settings = get_settings()
