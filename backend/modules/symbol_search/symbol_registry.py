"""
File path: backend/modules/symbol_search/symbol_registry.py
Purpose: SymbolRegistry — in-memory registry loaded from symbol_registry.json.
         Provides fast O(1) ticker lookup and prefix search without DB access.
         Used as fallback when DB is unavailable and by seed scripts.

Loaded once on module import; refreshed by calling reload().
"""
import json
import logging
import os
logger = logging.getLogger("app")

REGISTRY_PATH = os.path.join(
    os.path.dirname(__file__), "../../data/symbols/symbol_registry.json"
)

_registry: dict = {}
_loaded: bool = False


def load() -> dict:
    """Load symbol registry from JSON file. Called once on startup."""
    global _registry, _loaded
    try:
        with open(REGISTRY_PATH) as f:
            data = json.load(f)
        data.pop("_meta", None)
        _registry = {k.upper(): v for k, v in data.items()}
        _loaded = True
        logger.info(f"Symbol registry loaded: {len(_registry)} symbols")
    except FileNotFoundError:
        logger.warning(f"Symbol registry file not found: {REGISTRY_PATH}")
        _registry = {}
        _loaded = False
    return _registry


def get(ticker: str) -> dict | None:
    """
    Look up a ticker in the registry.
    Returns metadata dict or None if not found.
    """
    if not _loaded:
        load()
    return _registry.get(ticker.upper())


def search(query: str, limit: int = 10) -> list:
    """
    Search registry by ticker prefix or name substring.
    Returns list of {ticker, name, type, exchange, sector} dicts.
    """
    if not _loaded:
        load()
    query_upper = query.upper()
    query_lower = query.lower()
    results = []
    for ticker, meta in _registry.items():
        name = meta.get("name", "")
        if ticker.startswith(query_upper) or query_lower in name.lower():
            results.append({"ticker": ticker, **meta})
        if len(results) >= limit:
            break
    results.sort(key=lambda r: (0 if r["ticker"] == query_upper else 1, r["ticker"]))
    return results[:limit]


def all_tickers() -> list[str]:
    """Return list of all ticker symbols in registry."""
    if not _loaded:
        load()
    return list(_registry.keys())


def reload() -> dict:
    """Force reload registry from disk (e.g. after seed_symbol_registry.py runs)."""
    global _loaded
    _loaded = False
    return load()
