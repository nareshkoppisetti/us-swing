"""Populate symbol_registry.json from Yahoo Finance."""
import json, yfinance as yf
from pathlib import Path

CORE_SYMBOLS = {
    # Indices
    "SPY": {"name": "SPDR S&P 500 ETF Trust", "type": "etf", "exchange": "NYSE"},
    "QQQ": {"name": "Invesco QQQ Trust", "type": "etf", "exchange": "NASDAQ"},
    "DIA": {"name": "SPDR Dow Jones Industrial Average ETF", "type": "etf", "exchange": "NYSE"},
    "IWM": {"name": "iShares Russell 2000 ETF", "type": "etf", "exchange": "NYSE"},
    # Commodities (ETFs)
    "GLD": {"name": "SPDR Gold Shares", "type": "etf", "exchange": "NYSE"},
    "USO": {"name": "United States Oil Fund", "type": "etf", "exchange": "NYSE"},
    "SLV": {"name": "iShares Silver Trust", "type": "etf", "exchange": "NYSE"},
    "UNG": {"name": "United States Natural Gas Fund", "type": "etf", "exchange": "NYSE"},
    "CPER": {"name": "United States Copper Index Fund", "type": "etf", "exchange": "NYSE"},
    # Commodity Futures
    "GC=F": {"name": "Gold Futures", "type": "futures", "exchange": "CME"},
    "CL=F": {"name": "Crude Oil Futures", "type": "futures", "exchange": "NYMEX"},
    "NG=F": {"name": "Natural Gas Futures", "type": "futures", "exchange": "NYMEX"},
    "SI=F": {"name": "Silver Futures", "type": "futures", "exchange": "CME"},
    "HG=F": {"name": "Copper Futures", "type": "futures", "exchange": "CME"},
    # Sector ETFs
    "XLK": {"name": "Technology Select Sector SPDR", "type": "etf", "exchange": "NYSE"},
    "XLF": {"name": "Financial Select Sector SPDR", "type": "etf", "exchange": "NYSE"},
    "XLE": {"name": "Energy Select Sector SPDR", "type": "etf", "exchange": "NYSE"},
    "XLV": {"name": "Health Care Select Sector SPDR", "type": "etf", "exchange": "NYSE"},
    "XLI": {"name": "Industrial Select Sector SPDR", "type": "etf", "exchange": "NYSE"},
    "XLY": {"name": "Consumer Discretionary Select Sector SPDR", "type": "etf", "exchange": "NYSE"},
    "XLP": {"name": "Consumer Staples Select Sector SPDR", "type": "etf", "exchange": "NYSE"},
    "XLRE": {"name": "Real Estate Select Sector SPDR", "type": "etf", "exchange": "NYSE"},
    "XLU": {"name": "Utilities Select Sector SPDR", "type": "etf", "exchange": "NYSE"},
    "XLB": {"name": "Materials Select Sector SPDR", "type": "etf", "exchange": "NYSE"},
    "XLC": {"name": "Communication Services Select Sector SPDR", "type": "etf", "exchange": "NYSE"},
    # Dollar
    "UUP": {"name": "Invesco DB US Dollar Index Bullish Fund", "type": "etf", "exchange": "NYSE"},
}

OUT = Path("../backend/data/symbols/symbol_registry.json")

def seed():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    registry = dict(CORE_SYMBOLS)
    print(f"Writing {len(registry)} core symbols to {OUT}")
    OUT.write_text(json.dumps(registry, indent=2))
    print("Done.")

if __name__ == "__main__":
    seed()
