"""
File path: backend/modules/market_data/collectors/newsapi_collector.py
Purpose: NewsAPICollector — wraps NewsAPI REST. Key: NEWS_API_KEY. 100 req/day.
         Used by Agent 7 (News Analyst) as primary news source.
"""
import logging
from datetime import datetime, timedelta

import requests

from core.cache import cache_get, cache_set
from core.exceptions import RateLimitError
from modules.market_data.collectors.collector_base import CollectorBase

logger = logging.getLogger("app")

NEWS_API_BASE = "https://newsapi.org/v2/everything"
RATE_LIMIT_KEY = "rate_limit:newsapi"
RATE_LIMIT_MAX = 100
CACHE_TTL = 1800  # 30 minutes per symbol


class NewsAPICollector(CollectorBase):
    """NewsAPI REST client. 100 req/day free tier."""

    source_name = "NewsAPI"
    requires_api_key = True
    daily_request_limit = RATE_LIMIT_MAX

    def __init__(self):
        from config import settings
        self.api_key = settings.NEWS_API_KEY

    def _check_rate_limit(self):
        count = cache_get(RATE_LIMIT_KEY) or 0
        if int(count) >= RATE_LIMIT_MAX:
            raise RateLimitError("NewsAPI daily limit (100 requests) reached")

    def _increment_rate_limit(self):
        count = cache_get(RATE_LIMIT_KEY) or 0
        now = datetime.utcnow()
        midnight = now.replace(hour=23, minute=59, second=59)
        ttl = int((midnight - now).total_seconds()) + 1
        cache_set(RATE_LIMIT_KEY, int(count) + 1, ttl=ttl)

    def fetch(self, symbol: str, **kwargs) -> list:
        """Generic fetch — returns news articles."""
        company_name = kwargs.get("company_name", symbol)
        limit = kwargs.get("limit", 20)
        return self.fetch_news(symbol, company_name=company_name, limit=limit)

    def fetch_news(self, symbol: str, company_name: str = None, limit: int = 20) -> list:
        """
        Fetch recent news articles for a symbol from NewsAPI.
        Cache per symbol 30 minutes.
        Returns list of {title, source, url, published_at, content}
        """
        cache_key = f"news:{symbol}"
        cached = cache_get(cache_key)
        if cached is not None:
            return cached

        if not self.api_key:
            logger.warning("NEWS_API_KEY not configured")
            return []

        self._check_rate_limit()

        try:
            query = company_name or symbol
            # Use symbol as additional query term
            search_q = f"{query} OR {symbol}" if company_name and company_name != symbol else query

            since = (datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ")

            params = {
                "q": search_q,
                "from": since,
                "sortBy": "publishedAt",
                "language": "en",
                "pageSize": min(limit, 100),
                "apiKey": self.api_key,
            }

            response = requests.get(NEWS_API_BASE, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()

            if data.get("status") != "ok":
                logger.warning(f"NewsAPI status not ok: {data.get('message', 'Unknown error')}")
                return []

            self._increment_rate_limit()
            articles = []
            for item in data.get("articles", [])[:limit]:
                articles.append({
                    "title": item.get("title", ""),
                    "source": item.get("source", {}).get("name", ""),
                    "url": item.get("url", ""),
                    "published_at": item.get("publishedAt", ""),
                    "content": item.get("description") or item.get("content") or "",
                })

            cache_set(cache_key, articles, ttl=CACHE_TTL)
            logger.info(f"NewsAPI: fetched {len(articles)} articles for {symbol}")
            return articles

        except RateLimitError:
            raise
        except Exception as e:
            logger.error(f"NewsAPI fetch failed for {symbol}: {e}")
            return []
