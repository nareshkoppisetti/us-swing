"""
File path: backend/modules/market_data/collectors/alpha_vantage.py
Purpose: AlphaVantageCollector — wraps Alpha Vantage REST API.
         Key: ALPHA_VANTAGE_API_KEY. 25 req/day tracked via diskcache.
         Used as fallback for Yahoo Finance OHLCV.
"""
import logging
from datetime import datetime

import pandas as pd
import requests

from core.cache import cache_get, cache_set
from modules.market_data.collectors.collector_base import CollectorBase
from core.exceptions import RateLimitError

logger = logging.getLogger("app")

RATE_LIMIT_KEY = "rate_limit:alpha_vantage"
RATE_LIMIT_MAX = 25
BASE_URL = "https://www.alphavantage.co/query"


class AlphaVantageCollector(CollectorBase):
    """Alpha Vantage REST API client. 25 req/day free tier."""

    source_name = "Alpha Vantage REST API"
    requires_api_key = True
    daily_request_limit = RATE_LIMIT_MAX

    def __init__(self):
        from config import settings
        self.api_key = settings.ALPHA_VANTAGE_API_KEY

    def _check_rate_limit(self):
        """Raise RateLimitError if daily quota exceeded."""
        count = cache_get(RATE_LIMIT_KEY) or 0
        if int(count) >= RATE_LIMIT_MAX:
            raise RateLimitError("Alpha Vantage daily request limit (25) reached")

    def _increment_rate_limit(self):
        """Increment daily request counter. TTL = until end of day."""
        count = cache_get(RATE_LIMIT_KEY) or 0
        # Compute seconds until midnight UTC
        now = datetime.utcnow()
        midnight = now.replace(hour=23, minute=59, second=59)
        ttl = int((midnight - now).total_seconds()) + 1
        cache_set(RATE_LIMIT_KEY, int(count) + 1, ttl=ttl)

    def fetch(self, symbol: str, **kwargs) -> pd.DataFrame:
        """Fetch daily OHLCV via TIME_SERIES_DAILY_ADJUSTED."""
        outputsize = kwargs.get("outputsize", "full")
        return self.fetch_ohlcv(symbol, outputsize=outputsize)

    def fetch_ohlcv(self, symbol: str, outputsize: str = "full") -> pd.DataFrame:
        """
        Fetch daily OHLCV from Alpha Vantage TIME_SERIES_DAILY endpoint.
        Returns DataFrame with columns: date, open, high, low, close, volume.
        """
        if not self.api_key:
            raise ValueError("ALPHA_VANTAGE_API_KEY not configured")

        self._check_rate_limit()

        params = {
            "function": "TIME_SERIES_DAILY",
            "symbol": symbol,
            "outputsize": outputsize,
            "apikey": self.api_key,
        }

        try:
            response = requests.get(BASE_URL, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()

            if "Error Message" in data:
                raise ValueError(f"Alpha Vantage error: {data['Error Message']}")
            if "Note" in data:
                raise RateLimitError(f"Alpha Vantage rate limit note: {data['Note']}")

            time_series = data.get("Time Series (Daily)", {})
            if not time_series:
                raise ValueError(f"No time series data for {symbol}")

            self._increment_rate_limit()

            rows = []
            for date_str, values in time_series.items():
                rows.append({
                    "date": datetime.strptime(date_str, "%Y-%m-%d").date(),
                    "open": float(values.get("1. open", 0)),
                    "high": float(values.get("2. high", 0)),
                    "low": float(values.get("3. low", 0)),
                    "close": float(values.get("4. close", 0)),
                    "volume": int(values.get("5. volume", 0)),
                    "vwap": None,
                })

            df = pd.DataFrame(rows)
            df.sort_values("date", inplace=True)
            df.reset_index(drop=True, inplace=True)
            logger.info(f"Alpha Vantage: fetched {len(df)} rows for {symbol}")
            return df

        except RateLimitError:
            raise
        except Exception as e:
            logger.error(f"Alpha Vantage OHLCV fetch failed for {symbol}: {e}")
            raise
