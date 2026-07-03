"""
File path: backend/modules/market_data/collectors/yahoo_collector.py
Purpose: YahooFinanceCollector — wraps yfinance.download() and yfinance.Ticker().
         No API key required. Implements CollectorBase interface (SPEC Section 11.1).
"""
import logging
from datetime import datetime, timedelta
from typing import Optional

import pandas as pd
import yfinance as yf

from modules.market_data.collectors.collector_base import CollectorBase

logger = logging.getLogger("app")


class YahooFinanceCollector(CollectorBase):
    """Wraps yfinance. No API key required. Primary OHLCV source."""

    source_name = "Yahoo Finance (yfinance)"
    requires_api_key = False
    daily_request_limit = None

    def fetch(self, symbol: str, **kwargs) -> pd.DataFrame:
        """Generic fetch — delegates to fetch_ohlcv with kwargs."""
        period = kwargs.get("period", "1y")
        interval = kwargs.get("interval", "1d")
        return self.fetch_ohlcv(symbol, period=period, interval=interval)

    def fetch_ohlcv(self, symbol: str, period: str = "1y", interval: str = "1d",
                    start: Optional[str] = None, end: Optional[str] = None) -> pd.DataFrame:
        """
        Fetch OHLCV data using yfinance.download().
        Returns DataFrame with columns: date, open, high, low, close, volume.
        """
        try:
            ticker = yf.Ticker(symbol)
            if start and end:
                df = ticker.history(start=start, end=end, interval=interval, auto_adjust=True)
            else:
                df = ticker.history(period=period, interval=interval, auto_adjust=True)

            if df is None or df.empty:
                raise ValueError(f"No data returned for symbol {symbol}")

            df = df.reset_index()
            # Normalize column names
            df.columns = [c.lower() for c in df.columns]
            df.rename(columns={"date": "date"}, inplace=True)

            # Ensure date is date type (not datetime with tz)
            if "date" in df.columns:
                df["date"] = pd.to_datetime(df["date"]).dt.date
            elif "datetime" in df.columns:
                df["date"] = pd.to_datetime(df["datetime"]).dt.date
                df.drop(columns=["datetime"], errors="ignore", inplace=True)

            # Keep only needed columns
            keep_cols = ["date", "open", "high", "low", "close", "volume"]
            available = [c for c in keep_cols if c in df.columns]
            df = df[available].copy()

            # Add vwap as None (yfinance doesn't provide it for daily)
            df["vwap"] = None

            logger.info(f"Yahoo Finance: fetched {len(df)} rows for {symbol}")
            return df

        except Exception as e:
            logger.error(f"Yahoo Finance OHLCV fetch failed for {symbol}: {e}")
            raise

    def fetch_quote(self, symbol: str) -> dict:
        """
        Fetch current quote: price, change%, market cap, 52w high/low.
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info or {}

            current_price = (
                info.get("regularMarketPrice")
                or info.get("currentPrice")
                or info.get("previousClose", 0.0)
            )
            previous_close = info.get("regularMarketPreviousClose") or info.get("previousClose", current_price)
            change = current_price - previous_close if previous_close else 0.0
            change_pct = (change / previous_close * 100) if previous_close else 0.0

            return {
                "symbol": symbol,
                "price": float(current_price or 0),
                "change": float(change),
                "change_pct": float(change_pct),
                "volume": int(info.get("regularMarketVolume") or info.get("volume", 0)),
                "market_cap": info.get("marketCap"),
                "week52_high": info.get("fiftyTwoWeekHigh"),
                "week52_low": info.get("fiftyTwoWeekLow"),
                "name": info.get("longName") or info.get("shortName") or symbol,
                "sector": info.get("sector"),
                "industry": info.get("industry"),
                "asset_type": info.get("quoteType", "EQUITY"),
            }
        except Exception as e:
            logger.error(f"Yahoo Finance quote fetch failed for {symbol}: {e}")
            return {
                "symbol": symbol, "price": 0.0, "change": 0.0, "change_pct": 0.0,
                "volume": 0, "market_cap": None, "week52_high": None, "week52_low": None,
                "name": symbol, "sector": None, "industry": None, "asset_type": "EQUITY",
            }

    def fetch_options_chain(self, symbol: str) -> tuple:
        """
        Fetch options chain from yfinance.
        Returns (calls_df, puts_df).
        """
        try:
            ticker = yf.Ticker(symbol)
            expirations = ticker.options
            if not expirations:
                return pd.DataFrame(), pd.DataFrame()

            all_calls, all_puts = [], []
            # Fetch next 4 expirations max
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
            return calls_df, puts_df
        except Exception as e:
            logger.error(f"Yahoo Finance options chain failed for {symbol}: {e}")
            return pd.DataFrame(), pd.DataFrame()

    def fetch_news(self, symbol: str, limit: int = 20) -> list:
        """Fetch recent news articles for symbol from Yahoo Finance."""
        try:
            ticker = yf.Ticker(symbol)
            news = ticker.news or []
            articles = []
            for item in news[:limit]:
                articles.append({
                    "title": item.get("title", ""),
                    "source": item.get("publisher", ""),
                    "url": item.get("link", ""),
                    "published_at": datetime.utcfromtimestamp(
                        item.get("providerPublishTime", 0)
                    ).isoformat() if item.get("providerPublishTime") else None,
                    "summary": item.get("summary", ""),
                })
            return articles
        except Exception as e:
            logger.warning(f"Yahoo Finance news failed for {symbol}: {e}")
            return []

    def fetch_earnings(self, symbol: str) -> dict:
        """Fetch earnings calendar and history from Yahoo Finance."""
        try:
            ticker = yf.Ticker(symbol)
            calendar = ticker.calendar

            next_earnings_date = None
            if calendar is not None and not calendar.empty:
                try:
                    # calendar is a dict or DataFrame; try to extract date
                    if isinstance(calendar, dict):
                        dates = calendar.get("Earnings Date", [])
                        if dates:
                            next_earnings_date = str(dates[0])
                    elif hasattr(calendar, "columns"):
                        if "Earnings Date" in calendar.columns:
                            next_earnings_date = str(calendar["Earnings Date"].iloc[0])
                except Exception:
                    pass

            # Earnings history
            earnings = ticker.earnings_history if hasattr(ticker, "earnings_history") else None
            history = []
            if earnings is not None and not (hasattr(earnings, "empty") and earnings.empty):
                try:
                    if hasattr(earnings, "to_dict"):
                        records = earnings.reset_index().to_dict("records")
                        for r in records[-4:]:  # last 4 quarters
                            history.append({
                                "date": str(r.get("Earnings Date", r.get("date", ""))),
                                "eps_estimate": r.get("EPS Estimate", r.get("epsestimate")),
                                "eps_actual": r.get("Reported EPS", r.get("epsactual")),
                                "surprise_pct": r.get("Surprise(%)", r.get("epssurprisepct")),
                            })
                except Exception:
                    pass

            return {
                "next_earnings_date": next_earnings_date,
                "history": history,
            }
        except Exception as e:
            logger.warning(f"Yahoo Finance earnings failed for {symbol}: {e}")
            return {"next_earnings_date": None, "history": []}
