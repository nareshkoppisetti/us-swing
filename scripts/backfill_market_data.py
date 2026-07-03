#!/usr/bin/env python3
"""
File path: scripts/backfill_market_data.py
Purpose: Convenience wrapper — delegates to backend/scripts/backfill_market_data.py.
         Run from the project root: python scripts/backfill_market_data.py

Usage:
    python scripts/backfill_market_data.py [--symbols AAPL,SPY] [--days 1825]
"""
import subprocess
import sys
import os

script = os.path.join(os.path.dirname(__file__), "..", "backend", "scripts", "backfill_market_data.py")
result = subprocess.run([sys.executable, os.path.abspath(script)] + sys.argv[1:])
sys.exit(result.returncode)
