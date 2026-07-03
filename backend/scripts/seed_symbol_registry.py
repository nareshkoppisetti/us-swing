"""
File path: backend/scripts/seed_symbol_registry.py
Purpose: Seed the symbols database table from symbol_registry.json.
         Run after initial database migration to populate Symbol records.

Usage:
    cd backend
    python scripts/seed_symbol_registry.py

Steps:
  1. Read data/symbols/symbol_registry.json
  2. For each entry: upsert into symbols table (skip existing, update if changed)
  3. Log count of inserted vs updated vs skipped records
"""
import json
import logging
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

REGISTRY_FILE = "data/symbols/symbol_registry.json"


def main():
    """
    Load symbol_registry.json and upsert into DB.
    TODO: Implement after database module is complete.
    Steps:
      1. from core.database import SessionLocal
      2. from modules.market_data.models import Symbol
      3. db = SessionLocal()
      4. For each symbol in registry: db.merge(Symbol(...))
      5. db.commit()
    """
    with open(REGISTRY_FILE) as f:
        registry = json.load(f)

    registry.pop("_meta", {})
    logger.info(f"Found {len(registry)} symbols in registry.")
    logger.info("TODO: Insert into database once DB module is initialized.")

    for ticker, meta in registry.items():
        logger.debug(f"  {ticker}: {meta['name']} ({meta['type']})")

    logger.info("Seed complete (stub — implement DB insert).")


if __name__ == "__main__":
    main()
