"""
File path: backend/modules/market_data/collectors/stooq_collector.py
Purpose: StooqCollector — fetches OHLCV directly from Stooq's public CSV
         export endpoint. No API key needed. Secondary fallback for OHLCV
         after Alpha Vantage.

NOTE: pandas_datareader's built-in "stooq" data_source was removed from the
library (raises `NotImplementedError: data_source='stooq' is not
implemented` on pandas_datareader >= 0.10). We hit Stooq's CSV export URL
directly instead — it's the same underlying data, no API key, no extra
dependency.
"""
import io
import logging
from datetime import datetime, timedelta

import pandas as pd
import requests

from modules.market_data.collectors.collector_base import CollectorBase

logger = logging.getLogger("app")

STOOQ_CSV_URL = "https://stooq.com/q/d/l/"


class StooqCollector(CollectorBase):
    """Fetches OHLCV directly from Stooq's public CSV export. No API key needed."""

    source_name = "Stooq (CSV export)"
    requires_api_key = False
    daily_request_limit = None

    def fetch(self, symbol: str, **kwargs) -> pd.DataFrame:
        """Fetch OHLCV from Stooq."""
        start = kwargs.get("start", (datetime.today() - timedelta(days=365)).strftime("%Y-%m-%d"))
        end = kwargs.get("end", datetime.today().strftime("%Y-%m-%d"))
        return self.fetch_ohlcv(symbol, start=start, end=end)

    def fetch_ohlcv(self, symbol: str, start: str = None, end: str = None) -> pd.DataFrame:
        """
        Fetch daily OHLCV from Stooq's CSV export endpoint.
        Returns DataFrame with columns: date, open, high, low, close, volume, vwap.
        """
        try:
            if not start:
                start = (datetime.today() - timedelta(days=365)).strftime("%Y-%m-%d")
            if not end:
                end = datetime.today().strftime("%Y-%m-%d")

            # Stooq uses different ticker format for some symbols (e.g. futures)
            # and requires US tickers suffixed with ".US" for its CSV export.
            stooq_symbol = symbol.replace("=F", "").upper()
            if "." not in stooq_symbol and "^" not in stooq_symbol:
                stooq_symbol = f"{stooq_symbol}.US"

            params = {
                "s": stooq_symbol,
                "d1": start.replace("-", ""),
                "d2": end.replace("-", ""),
                "i": "d",  # daily interval
            }
            resp = requests.get(STOOQ_CSV_URL, params=params, timeout=10)
            resp.raise_for_status()

            text = resp.text.strip()
            if not text or text.lower().startswith("no data") or "<html" in text.lower():
                raise ValueError(f"No Stooq data for {symbol}")

            df = pd.read_csv(io.StringIO(text))
            if df is None or df.empty:
                raise ValueError(f"No Stooq data for {symbol}")

            df.columns = [c.lower() for c in df.columns]
            df["date"] = pd.to_datetime(df["date"]).dt.date
            df["vwap"] = None

            # Ensure required columns
            for col in ["open", "high", "low", "close", "volume"]:
                if col not in df.columns:
                    df[col] = None

            df.sort_values("date", inplace=True)
            df.reset_index(drop=True, inplace=True)
            logger.info(f"Stooq: fetched {len(df)} rows for {symbol}")
            return df

        except Exception as e:
            logger.error(f"Stooq OHLCV fetch failed for {symbol}: {e}")
            raise
