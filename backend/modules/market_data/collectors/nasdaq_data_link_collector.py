"""
File path: backend/modules/market_data/collectors/nasdaq_data_link_collector.py
Purpose: NasdaqDataLinkCollector — wraps Nasdaq Data Link (Quandl) free tier API.
         Key: NASDAQ_DATA_LINK_API_KEY.
         Used by commodity agents (35-42) for COT data.
"""
import logging

import pandas as pd
import requests

from core.cache import cache_get, cache_set
from modules.market_data.collectors.collector_base import CollectorBase

logger = logging.getLogger("app")

QUANDL_BASE_URL = "https://data.nasdaq.com/api/v3/datasets"
CACHE_TTL = 86400  # 24 hours

# COT dataset mapping (CFTC via Nasdaq Data Link)
COT_DATASET_MAP = {
    "CL=F": "CFTC/067651_FO_L_CHG",  # Crude Oil WTI
    "GC=F": "CFTC/088691_F_L_CHG",   # Gold
    "NG=F": "CFTC/023651_FO_L_CHG",  # Natural Gas
    "SI=F": "CFTC/084691_F_L_CHG",   # Silver
    "HG=F": "CFTC/085692_F_L_CHG",   # Copper
}


class NasdaqDataLinkCollector(CollectorBase):
    """Nasdaq Data Link (Quandl) free tier client."""

    source_name = "Nasdaq Data Link (Quandl)"
    requires_api_key = True
    daily_request_limit = None  # Free tier: 50 req/day but not strictly enforced

    def __init__(self):
        from config import settings
        self.api_key = settings.NASDAQ_DATA_LINK_API_KEY

    def fetch(self, symbol: str, **kwargs) -> pd.DataFrame:
        """Fetch COT data for symbol."""
        return self.fetch_cot_data(symbol)

    def fetch_cot_data(self, symbol: str) -> pd.DataFrame:
        """
        Fetch Commitment of Traders (COT) data for a commodity symbol.
        Used by Agents 35-42.
        Returns DataFrame with net positioning data or empty DataFrame if unavailable.
        """
        cache_key = f"quandl:cot:{symbol}"
        cached = cache_get(cache_key)
        if cached is not None:
            return cached

        dataset_code = COT_DATASET_MAP.get(symbol)
        if not dataset_code or not self.api_key:
            # Return empty frame if symbol not in COT map or no API key
            result = pd.DataFrame(columns=["date", "net_position", "long", "short"])
            cache_set(cache_key, result, ttl=CACHE_TTL)
            return result

        try:
            url = f"{QUANDL_BASE_URL}/{dataset_code}.json"
            params = {
                "api_key": self.api_key,
                "rows": 20,
            }
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()

            dataset = data.get("dataset", {})
            column_names = dataset.get("column_names", [])
            rows = dataset.get("data", [])

            if not rows:
                result = pd.DataFrame(columns=["date", "net_position", "long", "short"])
                cache_set(cache_key, result, ttl=CACHE_TTL)
                return result

            df = pd.DataFrame(rows, columns=column_names)
            df.columns = [c.lower().replace(" ", "_") for c in df.columns]

            # Extract date and net positioning
            if "date" in df.columns:
                df["date"] = pd.to_datetime(df["date"]).dt.date

            # Normalize column names for COT net position
            # COT reports typically have: non_commercial_longs, non_commercial_shorts
            long_col = next((c for c in df.columns if "long" in c and "non_commercial" in c), None)
            short_col = next((c for c in df.columns if "short" in c and "non_commercial" in c), None)

            if long_col and short_col:
                df["net_position"] = df[long_col] - df[short_col]
                df["long"] = df[long_col]
                df["short"] = df[short_col]
            else:
                df["net_position"] = None
                df["long"] = None
                df["short"] = None

            keep = ["date", "net_position", "long", "short"]
            available = [c for c in keep if c in df.columns]
            df = df[available].copy()
            df.sort_values("date", inplace=True, ascending=False)
            df.reset_index(drop=True, inplace=True)

            cache_set(cache_key, df, ttl=CACHE_TTL)
            logger.info(f"Nasdaq Data Link COT: fetched {len(df)} rows for {symbol}")
            return df

        except Exception as e:
            logger.warning(f"Nasdaq Data Link COT fetch failed for {symbol}: {e}")
            result = pd.DataFrame(columns=["date", "net_position", "long", "short"])
            cache_set(cache_key, result, ttl=CACHE_TTL)
            return result
