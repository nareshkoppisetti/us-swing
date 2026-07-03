"""
File path: backend/modules/market_data/collectors/fred_collector.py
Purpose: FREDCollector — wraps FRED REST API. Key: FRED_API_KEY. Unlimited rate.
         Used by macro agents (11, 12, 13) for economic series data.
"""
import logging
from datetime import datetime

import pandas as pd
import requests

from core.cache import cache_get, cache_set
from modules.market_data.collectors.collector_base import CollectorBase

logger = logging.getLogger("app")

FRED_BASE_URL = "https://api.stlouisfed.org/fred/series/observations"
CACHE_TTL = 86400  # 24 hours


class FREDCollector(CollectorBase):
    """FRED REST API client. Unlimited rate."""

    source_name = "FRED REST API"
    requires_api_key = True
    daily_request_limit = None

    def __init__(self):
        from config import settings
        self.api_key = settings.FRED_API_KEY

    def fetch(self, symbol: str, **kwargs) -> pd.DataFrame:
        """Fetch as DataFrame (series_id is the symbol)."""
        limit = kwargs.get("limit", 200)
        series = self.fetch_series(symbol, limit=limit)
        return series.to_frame(name="value").reset_index().rename(columns={"index": "date"})

    def fetch_series(self, series_id: str, limit: int = 200) -> pd.Series:
        """
        Fetch a FRED economic data series.
        Returns pd.Series indexed by date.
        Cache key: fred:{series_id}, TTL 24 hours.
        """
        cache_key = f"fred:{series_id}"
        cached = cache_get(cache_key)
        if cached is not None:
            return cached

        if not self.api_key:
            logger.warning("FRED_API_KEY not configured, returning empty series")
            return pd.Series(dtype=float, name=series_id)

        try:
            params = {
                "series_id": series_id,
                "api_key": self.api_key,
                "file_type": "json",
                "limit": limit,
                "sort_order": "desc",
            }
            response = requests.get(FRED_BASE_URL, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()

            observations = data.get("observations", [])
            records = {}
            for obs in observations:
                if obs.get("value") not in (".", "", None):
                    try:
                        records[datetime.strptime(obs["date"], "%Y-%m-%d").date()] = float(obs["value"])
                    except (ValueError, KeyError):
                        pass

            series = pd.Series(records, name=series_id, dtype=float)
            series.sort_index(inplace=True)
            cache_set(cache_key, series, ttl=CACHE_TTL)
            logger.info(f"FRED: fetched {len(series)} observations for {series_id}")
            return series

        except Exception as e:
            logger.error(f"FRED fetch failed for {series_id}: {e}")
            return pd.Series(dtype=float, name=series_id)
