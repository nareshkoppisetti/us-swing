"""
File path: backend/modules/market_data/collectors/eia_collector.py
Purpose: EIACollector — wraps EIA REST API for energy data.
         Key: EIA_API_KEY. Unlimited rate.
         Used by Agent 35 (crude oil) and Agent 37 (natural gas).
"""
import logging
import requests

from core.cache import cache_get, cache_set
from modules.market_data.collectors.collector_base import CollectorBase

logger = logging.getLogger("app")

EIA_BASE_URL = "https://api.eia.gov/v2"
CACHE_TTL = 86400  # 24 hours


class EIACollector(CollectorBase):
    """EIA energy data API client. Unlimited rate."""

    source_name = "EIA Energy Data API"
    requires_api_key = True
    daily_request_limit = None

    def __init__(self):
        from config import settings
        self.api_key = settings.EIA_API_KEY

    def fetch(self, symbol: str, **kwargs) -> dict:
        """Generic fetch — delegates based on symbol."""
        if "crude" in symbol.lower() or symbol in ("CL=F", "USO"):
            return self.fetch_petroleum_inventories()
        return self.fetch_natural_gas_storage()

    def fetch_petroleum_inventories(self) -> dict:
        """
        Fetch weekly crude oil inventory levels from EIA.
        Used by Agent 35. Cache 24 hours.
        Returns dict: {change, level, date, yoy_change}
        """
        cache_key = "eia:petroleum_inventories"
        cached = cache_get(cache_key)
        if cached is not None:
            return cached

        if not self.api_key:
            logger.warning("EIA_API_KEY not configured")
            return self._empty_petroleum_response()

        try:
            # Weekly U.S. Ending Stocks of Crude Oil
            params = {
                "api_key": self.api_key,
                "frequency": "weekly",
                "data[0]": "value",
                "facets[series][]": "WCRSTUS1",
                "sort[0][column]": "period",
                "sort[0][direction]": "desc",
                "length": 10,
                "offset": 0,
            }
            url = f"{EIA_BASE_URL}/petroleum/stoc/wstk/data/"
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()

            rows = data.get("response", {}).get("data", [])
            if len(rows) < 2:
                return self._empty_petroleum_response()

            current = float(rows[0].get("value", 0))
            previous = float(rows[1].get("value", 0))
            change = current - previous

            result = {
                "level": current,
                "change": change,
                "date": rows[0].get("period", ""),
                "yoy_change": None,
                "source": "EIA",
            }
            cache_set(cache_key, result, ttl=CACHE_TTL)
            return result

        except Exception as e:
            logger.error(f"EIA petroleum inventories fetch failed: {e}")
            return self._empty_petroleum_response()

    def fetch_natural_gas_storage(self) -> dict:
        """
        Fetch weekly natural gas storage from EIA.
        Used by Agent 37. Cache 24 hours.
        """
        cache_key = "eia:natural_gas_storage"
        cached = cache_get(cache_key)
        if cached is not None:
            return cached

        if not self.api_key:
            logger.warning("EIA_API_KEY not configured")
            return self._empty_gas_response()

        try:
            params = {
                "api_key": self.api_key,
                "frequency": "weekly",
                "data[0]": "value",
                "facets[series][]": "NW2_EPG0_SWO_R48_BCF",
                "sort[0][column]": "period",
                "sort[0][direction]": "desc",
                "length": 10,
                "offset": 0,
            }
            url = f"{EIA_BASE_URL}/natural-gas/stor/wkly/data/"
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()

            rows = data.get("response", {}).get("data", [])
            if len(rows) < 2:
                return self._empty_gas_response()

            current = float(rows[0].get("value", 0))
            previous = float(rows[1].get("value", 0))
            change = current - previous

            result = {
                "level": current,
                "change": change,
                "date": rows[0].get("period", ""),
                "yoy_change": None,
                "source": "EIA",
            }
            cache_set(cache_key, result, ttl=CACHE_TTL)
            return result

        except Exception as e:
            logger.error(f"EIA natural gas storage fetch failed: {e}")
            return self._empty_gas_response()

    def _empty_petroleum_response(self) -> dict:
        return {"level": None, "change": None, "date": None, "yoy_change": None, "source": "EIA_UNAVAILABLE"}

    def _empty_gas_response(self) -> dict:
        return {"level": None, "change": None, "date": None, "yoy_change": None, "source": "EIA_UNAVAILABLE"}
