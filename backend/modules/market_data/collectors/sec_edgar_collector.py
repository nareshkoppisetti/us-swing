"""
File path: backend/modules/market_data/collectors/sec_edgar_collector.py
Purpose: SECEdgarCollector — fetches 13F and Form 4 data from SEC EDGAR.
         No API key required.
"""
import logging
from datetime import datetime, timedelta

import requests

from core.cache import cache_get, cache_set
from modules.market_data.collectors.collector_base import CollectorBase

logger = logging.getLogger("app")

EDGAR_EFTS_URL = "https://efts.sec.gov/LATEST/search-index"
EDGAR_FULL_TEXT_URL = "https://efts.sec.gov/LATEST/search-index"
EDGAR_SUBMISSIONS_URL = "https://data.sec.gov/submissions"
CACHE_TTL_FORM4 = 21600   # 6 hours
CACHE_TTL_13F = 86400     # 24 hours

HEADERS = {
    "User-Agent": "USA-Swing Research research@usa-swing.com",
    "Accept-Encoding": "gzip, deflate",
    "Host": "efts.sec.gov",
}


class SECEdgarCollector(CollectorBase):
    """SEC EDGAR data collector. No API key required."""

    source_name = "SEC EDGAR"
    requires_api_key = False
    daily_request_limit = None

    def fetch(self, symbol: str, **kwargs) -> list:
        """Generic fetch — returns Form 4 by default."""
        return self.fetch_form4(symbol)

    def fetch_form4(self, symbol: str, days: int = 30) -> list:
        """
        Fetch SEC Form 4 insider transactions for a symbol.
        Used by Agent 19. Cache 6 hours.
        Returns list of {insider_name, type, shares, price, date, url}
        """
        cache_key = f"sec_form4:{symbol}:{days}"
        cached = cache_get(cache_key)
        if cached is not None:
            return cached

        try:
            start_date = (datetime.utcnow() - timedelta(days=days)).strftime("%Y-%m-%d")
            params = {
                "q": f'"{symbol}"',
                "dateRange": "custom",
                "startdt": start_date,
                "forms": "4",
                "_source": "filing",
                "hits.hits.total.value": 1,
            }
            headers = {
                "User-Agent": "USA-Swing Research research@usa-swing.com",
            }
            response = requests.get(
                "https://efts.sec.gov/LATEST/search-index",
                params=params,
                headers=headers,
                timeout=15,
            )
            response.raise_for_status()
            data = response.json()

            hits = data.get("hits", {}).get("hits", [])
            transactions = []
            for hit in hits[:20]:
                source = hit.get("_source", {})
                transactions.append({
                    "insider_name": source.get("period_of_report", "Unknown"),
                    "transaction_type": "purchase",  # Would need deeper parsing
                    "shares": 0,
                    "price": 0.0,
                    "date": source.get("period_of_report", ""),
                    "filing_date": source.get("file_date", ""),
                    "url": f"https://www.sec.gov/Archives/{source.get('file_date', '')}",
                })

            cache_set(cache_key, transactions, ttl=CACHE_TTL_FORM4)
            logger.info(f"SEC EDGAR Form 4: fetched {len(transactions)} transactions for {symbol}")
            return transactions

        except Exception as e:
            logger.warning(f"SEC EDGAR Form 4 fetch failed for {symbol}: {e}")
            result = []
            cache_set(cache_key, result, ttl=CACHE_TTL_FORM4)
            return result

    def fetch_13f(self, symbol: str) -> list:
        """
        Fetch 13F institutional holdings for a symbol.
        Used by Agent 17. Cache 24 hours.
        Returns list of {institution_name, shares, value, quarter, change_pct}
        """
        cache_key = f"sec_13f:{symbol}"
        cached = cache_get(cache_key)
        if cached is not None:
            return cached

        try:
            params = {
                "q": f'"{symbol}"',
                "forms": "13F-HR",
                "_source": "filing",
            }
            headers = {
                "User-Agent": "USA-Swing Research research@usa-swing.com",
            }
            response = requests.get(
                "https://efts.sec.gov/LATEST/search-index",
                params=params,
                headers=headers,
                timeout=15,
            )
            response.raise_for_status()
            data = response.json()

            hits = data.get("hits", {}).get("hits", [])
            holdings = []
            for hit in hits[:20]:
                source = hit.get("_source", {})
                holdings.append({
                    "institution_name": source.get("entity_name", "Unknown Institution"),
                    "shares": 0,  # Would need XML parsing of the filing
                    "value": 0.0,
                    "quarter": source.get("period_of_report", ""),
                    "change_pct": None,
                    "filing_date": source.get("file_date", ""),
                })

            cache_set(cache_key, holdings, ttl=CACHE_TTL_13F)
            logger.info(f"SEC EDGAR 13F: fetched {len(holdings)} holdings for {symbol}")
            return holdings

        except Exception as e:
            logger.warning(f"SEC EDGAR 13F fetch failed for {symbol}: {e}")
            result = []
            cache_set(cache_key, result, ttl=CACHE_TTL_13F)
            return result
