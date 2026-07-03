"""
File path: backend/scripts/backfill_market_data.py
Purpose: One-time script to backfill 5 years of OHLCV data for all symbols
         in the symbol registry. Run once before initial deployment.

Usage:
    cd backend
    python scripts/backfill_market_data.py [--symbols AAPL,SPY] [--days 1825]

Steps:
  1. Load all symbols from data/symbols/symbol_registry.json
  2. For each symbol: fetch 5 years of daily OHLCV via YahooFinanceCollector
  3. Validate with DataValidator
  4. Store to Parquet at data/market_data/ohlcv/{symbol}/daily.parquet
  5. Log success/failure per symbol

Estimated runtime: ~30-60 min for full universe (~500 symbols)
Rate limit protection: 0.5s sleep between symbols (Yahoo Finance)
"""
import argparse
import json
import logging
import time
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

REGISTRY_FILE = "data/symbols/symbol_registry.json"
DEFAULT_DAYS = 1825  # 5 years


def backfill_symbol(symbol: str, days: int):
    """
    Fetch and store OHLCV for a single symbol.
    TODO: Implement using YahooFinanceCollector + DataValidator + MarketDataService
    """
    raise NotImplementedError(f"backfill_symbol({symbol}) not yet implemented")


def main():
    parser = argparse.ArgumentParser(description="Backfill historical OHLCV data")
    parser.add_argument("--symbols", type=str, help="Comma-separated tickers (default: all)")
    parser.add_argument("--days", type=int, default=DEFAULT_DAYS, help="Days of history")
    args = parser.parse_args()

    with open(REGISTRY_FILE) as f:
        registry = json.load(f)

    registry.pop("_meta", {})
    symbols = args.symbols.split(",") if args.symbols else list(registry.keys())
    logger.info(f"Backfilling {len(symbols)} symbols x {args.days} days")

    success, failed = 0, []
    for i, symbol in enumerate(symbols, 1):
        logger.info(f"[{i}/{len(symbols)}] {symbol}...")
        try:
            backfill_symbol(symbol, args.days)
            success += 1
        except Exception as e:
            logger.error(f"Failed {symbol}: {e}")
            failed.append(symbol)
        time.sleep(0.5)

    logger.info(f"Done. {success}/{len(symbols)} succeeded. Failed: {failed}")


if __name__ == "__main__":
    main()
