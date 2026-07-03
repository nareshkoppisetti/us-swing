"""
File path: backend/core/cache.py
Purpose: Diskcache-based caching layer. Provides a singleton Cache instance
         and helper functions used across the platform.

SPEC Reference: Section 10.1 (Cache Layer — diskcache MVP)
BUILD_PLAN Reference: Phase 1.5

Cache key conventions:
  ohlcv:{symbol}:{timeframe}:{date}   — OHLCV DataFrames
  indicators:{symbol}:{date}          — Technical indicators
  options:{symbol}:{date}             — Options chain snapshots
  sentiment:{symbol}:{hours}          — News sentiment aggregates
  agent_output:{agent_id}:{symbol}:{date} — Latest agent outputs
  prediction:{symbol}:{horizon}:{date}    — Prediction results
  rate_limit:{key}                    — Rate limit counters (set by middleware)
"""

import logging
import os
import pickle
from typing import Any

import diskcache

from config import settings

logger = logging.getLogger("app")

_cache: diskcache.Cache | None = None


def get_cache() -> diskcache.Cache:
    """
    Return the singleton diskcache.Cache instance.
    Creates it on first call using CACHE_DIR from settings.
    """
    global _cache
    if _cache is None:
        _cache = init_cache()
    return _cache


def init_cache() -> diskcache.Cache:
    """
    Initialize the disk cache. Called from main.py lifespan startup.
    Returns the Cache instance so it can be passed to middleware.
    """
    global _cache
    os.makedirs(settings.CACHE_DIR, exist_ok=True)
    _cache = diskcache.Cache(
        settings.CACHE_DIR,
        size_limit=2 * 1024 ** 3,    # 2 GB max disk usage
        disk_min_file_size=0,         # cache everything on disk (not memory-mapped)
        statistics=False,             # disable stat tracking for performance
    )
    logger.info(f"Cache initialized at {settings.CACHE_DIR} (2GB limit)")
    return _cache


# ── Typed helpers ─────────────────────────────────────────────────────────────

def cache_get(key: str) -> Any | None:
    """
    Retrieve a value from cache by key.
    Returns None if key is missing or expired.
    """
    try:
        return get_cache().get(key)
    except Exception as e:
        logger.warning(f"cache_get failed for key={key}: {e}")
        return None


def cache_set(key: str, value: Any, ttl: int | None = None) -> bool:
    """
    Store a value in cache with optional TTL (seconds).
    Falls back to settings.CACHE_DEFAULT_TTL if ttl is not provided.
    Returns True on success.
    """
    try:
        expire = ttl if ttl is not None else settings.CACHE_DEFAULT_TTL
        get_cache().set(key, value, expire=expire)
        return True
    except Exception as e:
        logger.warning(f"cache_set failed for key={key}: {e}")
        return False


def cache_delete(key: str) -> bool:
    """Delete a key from cache. Returns True if key existed."""
    try:
        return get_cache().delete(key)
    except Exception as e:
        logger.warning(f"cache_delete failed for key={key}: {e}")
        return False


def cache_clear_prefix(prefix: str) -> int:
    """
    Delete all keys starting with the given prefix.
    Returns count of deleted keys.
    Useful for invalidating all cache for a symbol: cache_clear_prefix("ohlcv:AAPL:")
    """
    cache = get_cache()
    deleted = 0
    try:
        for key in list(cache.iterkeys()):
            if isinstance(key, str) and key.startswith(prefix):
                cache.delete(key)
                deleted += 1
    except Exception as e:
        logger.warning(f"cache_clear_prefix failed for prefix={prefix}: {e}")
    return deleted


# ── TTL constants (seconds) ───────────────────────────────────────────────────

TTL_OHLCV_DAILY    = 3_600      # 1 hour  — daily bars
TTL_OHLCV_INTRADAY = 300        # 5 min   — intraday bars
TTL_OPTIONS        = 600        # 10 min  — options chains
TTL_SENTIMENT      = 1_800      # 30 min  — news sentiment
TTL_INDICATORS     = 3_600      # 1 hour  — TA indicators
TTL_AGENT_OUTPUT   = 900        # 15 min  — agent outputs
TTL_PREDICTION     = 1_800      # 30 min  — predictions
TTL_SYMBOL_SEARCH  = 86_400     # 1 day   — symbol search results
