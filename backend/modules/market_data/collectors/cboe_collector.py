"""
File path: backend/modules/market_data/collectors/cboe_collector.py
Purpose: CBOECollector — fetches VIX data and options from CBOE via Yahoo Finance.
         No API key required for MVP. Used by strength and options agents.
"""
import logging

import pandas as pd
import yfinance as yf

from core.cache import cache_get, cache_set
from modules.market_data.collectors.collector_base import CollectorBase

logger = logging.getLogger("app")

VIX_CACHE_TTL = 900   # 15 minutes
OPTIONS_CACHE_TTL = 900  # 15 minutes


class CBOECollector(CollectorBase):
    """CBOE data via Yahoo Finance public data. No API key needed."""

    source_name = "CBOE (via Yahoo Finance)"
    requires_api_key = False
    daily_request_limit = None

    def fetch(self, symbol: str, **kwargs) -> dict:
        """Generic — returns VIX data."""
        return self.fetch_vix_data()

    def fetch_vix_data(self) -> dict:
        """
        Fetch current VIX, VIX9D, VIX3M levels and term structure.
        Used by Agent 26 (VIX Structure) and Agent 24 (Uncertainty).
        Cache 15 minutes.
        """
        cache_key = "cboe:vix_data"
        cached = cache_get(cache_key)
        if cached is not None:
            return cached

        try:
            vix_symbols = ["^VIX", "^VIX9D", "^VXV", "^VIX6M"]
            vix_data = {}

            for sym in vix_symbols:
                try:
                    ticker = yf.Ticker(sym)
                    info = ticker.info or {}
                    price = (
                        info.get("regularMarketPrice")
                        or info.get("currentPrice")
                        or info.get("previousClose")
                    )
                    if price is None:
                        # Fallback: grab last close from history
                        hist = ticker.history(period="5d")
                        price = float(hist["Close"].iloc[-1]) if not hist.empty else None
                    vix_data[sym] = float(price) if price else None
                except Exception:
                    vix_data[sym] = None

            vix = vix_data.get("^VIX")
            vix9d = vix_data.get("^VIX9D")
            vix3m = vix_data.get("^VXV")
            vix6m = vix_data.get("^VIX6M")

            # Determine term structure
            if vix9d is not None and vix3m is not None:
                if vix9d < vix3m:
                    term_structure = "contango"
                elif vix9d > vix3m:
                    term_structure = "backwardation"
                else:
                    term_structure = "flat"
            else:
                term_structure = "unknown"

            result = {
                "vix": vix,
                "vix9d": vix9d,
                "vix3m": vix3m,
                "vix6m": vix6m,
                "term_structure": term_structure,
                "source": "CBOE_via_Yahoo",
            }

            cache_set(cache_key, result, ttl=VIX_CACHE_TTL)
            logger.info(f"CBOE VIX data: VIX={vix}, VIX9D={vix9d}, VIX3M={vix3m}, structure={term_structure}")
            return result

        except Exception as e:
            logger.error(f"CBOE VIX data fetch failed: {e}")
            return {
                "vix": None, "vix9d": None, "vix3m": None,
                "term_structure": "unknown", "source": "CBOE_UNAVAILABLE",
            }

    def fetch_options_chain(self, symbol: str) -> tuple:
        """
        Fetch options chain via yfinance (CBOE proxy).
        Returns (calls_df, puts_df).
        """
        cache_key = f"cboe:options:{symbol}"
        cached = cache_get(cache_key)
        if cached is not None:
            return cached

        try:
            ticker = yf.Ticker(symbol)
            expirations = ticker.options
            if not expirations:
                result = (pd.DataFrame(), pd.DataFrame())
                cache_set(cache_key, result, ttl=OPTIONS_CACHE_TTL)
                return result

            all_calls, all_puts = [], []
            for exp in expirations[:4]:
                try:
                    chain = ticker.option_chain(exp)
                    calls = chain.calls.copy()
                    puts = chain.puts.copy()
                    calls["expiration"] = exp
                    puts["expiration"] = exp
                    all_calls.append(calls)
                    all_puts.append(puts)
                except Exception:
                    pass

            calls_df = pd.concat(all_calls, ignore_index=True) if all_calls else pd.DataFrame()
            puts_df = pd.concat(all_puts, ignore_index=True) if all_puts else pd.DataFrame()
            result = (calls_df, puts_df)
            cache_set(cache_key, result, ttl=OPTIONS_CACHE_TTL)
            return result

        except Exception as e:
            logger.error(f"CBOE options chain failed for {symbol}: {e}")
            return pd.DataFrame(), pd.DataFrame()
