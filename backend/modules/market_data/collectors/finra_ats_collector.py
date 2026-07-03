"""
File path: backend/modules/market_data/collectors/finra_ats_collector.py
Purpose: FINRAATSCollector — fetches FINRA ATS weekly aggregate data.
         No API key required. Always operates in degraded mode (MVP).
         Used by Agent 16 (Dark Pool Flow).
"""
import logging
import requests

from core.cache import cache_get, cache_set
from modules.market_data.collectors.collector_base import CollectorBase

logger = logging.getLogger("app")

CACHE_TTL = 86400  # 24 hours


class FINRAATSCollector(CollectorBase):
    """FINRA ATS weekly aggregate data. Always degraded mode in MVP."""

    source_name = "FINRA ATS (Aggregate)"
    requires_api_key = False
    daily_request_limit = None

    def fetch(self, symbol: str, **kwargs) -> dict:
        """Fetch ATS volume for symbol."""
        return self.fetch_ats_volume(symbol)

    def fetch_ats_volume(self, symbol: str) -> dict:
        """
        Fetch weekly ATS volume for a symbol vs 4-week average.
        Used by Agent 16. Always sets is_degraded=True.
        Returns dict: {symbol, weekly_volume, avg_volume_4w, volume_ratio, is_degraded}
        """
        cache_key = f"finra_ats:{symbol}"
        cached = cache_get(cache_key)
        if cached is not None:
            return cached

        # FINRA publishes weekly ATS data in CSV format
        # For MVP: return a neutral degraded signal since we can't parse weekly CSV reliably
        # Production upgrade: parse FINRA Weekly ATS Transparency Data CSVs
        result = {
            "symbol": symbol,
            "weekly_volume": None,
            "avg_volume_4w": None,
            "volume_ratio": 1.0,  # Neutral
            "accumulation_score": 50.0,
            "distribution_score": 50.0,
            "is_degraded": True,
            "source": "FINRA_ATS_DEGRADED",
            "note": "MVP degraded mode: FINRA provides aggregate-only weekly data. Full dark pool data requires Unusual Whales API.",
        }

        cache_set(cache_key, result, ttl=CACHE_TTL)
        logger.info(f"FINRA ATS: returning degraded signal for {symbol}")
        return result
