"""
File path: backend/modules/symbol_search/service.py
Purpose: SymbolSearchService — fast symbol lookup and search.
         Supports autocomplete and full-text search across ticker and name.

Search strategy (per SPEC):
  1. Exact ticker match (highest priority)
  2. Ticker prefix match (e.g. "APP" → AAPL, APPS)
  3. Company name ILIKE match (e.g. "apple" → Apple Inc.)
  4. Fallback: in-memory fuzzy match from symbol_registry.json

All results are sorted by: exact match first, then by market cap proxy (symbol type priority).
"""
import json
import logging
import os
from sqlalchemy.orm import Session
logger = logging.getLogger("app")

REGISTRY_FILE = os.path.join(os.path.dirname(__file__), "../../data/symbols/symbol_registry.json")


class SymbolSearchService:
    """
    Provides fast symbol search with fallback to in-memory registry.
    """

    def __init__(self, db: Session):
        self.db = db
        self._registry_cache: dict | None = None

    def search(self, query: str, limit: int = 10) -> list:
        """
        Search symbols by ticker prefix or company name.

        Returns:
            List of SymbolSearchResult-compatible dicts, sorted by relevance.

        Strategy:
          1. Try DB query (symbols table) with ILIKE on ticker and name
          2. Fallback to in-memory registry if DB unavailable
        TODO: Implement DB query, then fallback.
        """
        # Fallback: in-memory search from registry JSON
        return self._search_registry(query.upper(), limit)

    def _search_registry(self, query: str, limit: int) -> list:
        """In-memory search from symbol_registry.json. Used as DB fallback."""
        registry = self._load_registry()
        results = []
        for ticker, meta in registry.items():
            name = meta.get("name", "")
            if ticker.startswith(query) or query.lower() in name.lower():
                results.append({
                    "ticker": ticker,
                    "name": name,
                    "symbol_type": meta.get("type", "stock"),
                    "exchange": meta.get("exchange"),
                    "sector": meta.get("sector"),
                })
            if len(results) >= limit:
                break
        # Exact ticker matches first
        results.sort(key=lambda r: (0 if r["ticker"] == query else 1, r["ticker"]))
        return results[:limit]

    def _load_registry(self) -> dict:
        """Load and cache symbol_registry.json."""
        if self._registry_cache is None:
            try:
                with open(REGISTRY_FILE) as f:
                    data = json.load(f)
                data.pop("_meta", None)
                self._registry_cache = data
            except FileNotFoundError:
                logger.warning(f"Symbol registry not found at {REGISTRY_FILE}")
                self._registry_cache = {}
        return self._registry_cache

    def get_symbol(self, ticker: str) -> dict | None:
        """
        Get details for a single ticker.
        TODO: Query symbols table first, fallback to registry.
        """
        registry = self._load_registry()
        if ticker.upper() in registry:
            meta = registry[ticker.upper()]
            return {
                "ticker": ticker.upper(),
                "name": meta.get("name"),
                "symbol_type": meta.get("type"),
                "exchange": meta.get("exchange"),
                "sector": meta.get("sector"),
                "is_active": True,
            }
        return None

    def list_symbols(self, symbol_type: str = None, page: int = 1, page_size: int = 50) -> dict:
        """
        List all symbols with optional type filter and pagination.
        TODO: Query symbols table with filter + pagination.
        Fallback: return from registry.
        """
        registry = self._load_registry()
        items = []
        for ticker, meta in registry.items():
            if symbol_type and meta.get("type") != symbol_type:
                continue
            items.append({
                "ticker": ticker,
                "name": meta.get("name"),
                "symbol_type": meta.get("type"),
                "exchange": meta.get("exchange"),
                "sector": meta.get("sector"),
                "is_active": True,
            })
        start = (page - 1) * page_size
        return {
            "items": items[start:start + page_size],
            "total": len(items),
            "page": page,
            "page_size": page_size,
        }
