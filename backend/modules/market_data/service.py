"""
File path: backend/modules/market_data/service.py
Purpose: MarketDataService — orchestrates data collection, validation, and Parquet storage.
         Per SPEC Section 11.1 and BUILD_PLAN Phase 2.4.

Key responsibilities:
  - get_ohlcv(symbol, timeframe, period) → pd.DataFrame
    (tries Yahoo first, Alpha Vantage backup, Stooq fallback)
  - get_quote(symbol) → dict
  - get_options_chain(symbol) → tuple
  - get_vix_data() → dict
  - update_parquet(symbol, new_df, timeframe) — append-only
  - fetch_indicators(symbol) → dict of TA values

Collector priority per SPEC Section 11.1:
  Yahoo Finance → Alpha Vantage → Stooq (for OHLCV)
"""
import logging
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

from config import settings
from core.cache import cache_get, cache_set
from core.exceptions import DataUnavailableError
from modules.market_data.collectors.yahoo_collector import YahooFinanceCollector
from modules.market_data.collectors.alpha_vantage import AlphaVantageCollector
from modules.market_data.collectors.stooq_collector import StooqCollector
from modules.market_data.collectors.cboe_collector import CBOECollector
from modules.market_data.validators import DataValidator

logger = logging.getLogger("app")

OHLCV_CACHE_TTL = 3600      # 1 hour
QUOTE_CACHE_TTL = 300       # 5 minutes
OPTIONS_CACHE_TTL = 900     # 15 minutes


class MarketDataService:
    """
    Orchestrates data collection, validation, and Parquet storage.
    All methods follow: check cache → check Parquet → fetch from API.
    """

    def __init__(self, db=None, cache=None):
        self.db = db
        self.yahoo = YahooFinanceCollector()
        self.alpha_vantage = AlphaVantageCollector()
        self.stooq = StooqCollector()
        self.cboe = CBOECollector()
        self.validator = DataValidator()
        self._parquet_dir = Path(settings.PARQUET_DATA_DIR) / "ohlcv"

    # ── OHLCV ─────────────────────────────────────────────────────────────────

    def get_ohlcv(self, symbol: str, timeframe: str = "daily", period: str = "1y",
                  days: int = None) -> pd.DataFrame:
        """
        Fetch OHLCV for symbol.
        Strategy: cache → Parquet → Yahoo → Alpha Vantage → Stooq.
        Returns DataFrame: date, open, high, low, close, volume, vwap.
        """
        # Normalize period to days
        if days is None:
            period_map = {"1d": 1, "5d": 5, "1mo": 30, "3mo": 90, "6mo": 180,
                          "1y": 365, "2y": 730, "5y": 1825}
            days = period_map.get(period, 365)

        cache_key = f"ohlcv:{symbol}:{timeframe}"
        cached = cache_get(cache_key)
        if cached is not None and isinstance(cached, pd.DataFrame) and not cached.empty:
            return self._filter_by_days(cached, days)

        # Try Parquet
        try:
            df = self._load_parquet(symbol, timeframe)
            if df is not None and not df.empty:
                # Check if Parquet data is fresh enough (within 24h of latest trading day)
                if self._is_parquet_fresh(df):
                    cache_set(cache_key, df, ttl=OHLCV_CACHE_TTL)
                    return self._filter_by_days(df, days)
        except Exception:
            pass

        # Fetch from APIs
        df = self._fetch_ohlcv_with_fallback(symbol, period=period)
        if df is not None and not df.empty:
            df = self.validator.validate_ohlcv(df, symbol)
            self._update_parquet(symbol, df, timeframe)
            cache_set(cache_key, df, ttl=OHLCV_CACHE_TTL)
            return self._filter_by_days(df, days)

        raise DataUnavailableError(f"OHLCV data unavailable for {symbol}")

    def _fetch_ohlcv_with_fallback(self, symbol: str, period: str = "1y") -> Optional[pd.DataFrame]:
        """Try Yahoo → Alpha Vantage → Stooq."""
        # Yahoo Finance (primary)
        try:
            df = self.yahoo.fetch_ohlcv(symbol, period=period)
            if df is not None and not df.empty:
                logger.info(f"MarketDataService: fetched OHLCV for {symbol} from Yahoo Finance")
                return df
        except Exception as e:
            logger.warning(f"Yahoo Finance OHLCV failed for {symbol}: {e}")

        # Alpha Vantage (secondary)
        try:
            df = self.alpha_vantage.fetch_ohlcv(symbol, outputsize="full")
            if df is not None and not df.empty:
                logger.info(f"MarketDataService: fetched OHLCV for {symbol} from Alpha Vantage")
                return df
        except Exception as e:
            logger.warning(f"Alpha Vantage OHLCV failed for {symbol}: {e}")

        # Stooq (fallback)
        try:
            start = (datetime.today() - timedelta(days=730)).strftime("%Y-%m-%d")
            end = datetime.today().strftime("%Y-%m-%d")
            df = self.stooq.fetch_ohlcv(symbol, start=start, end=end)
            if df is not None and not df.empty:
                logger.info(f"MarketDataService: fetched OHLCV for {symbol} from Stooq")
                return df
        except Exception as e:
            logger.warning(f"Stooq OHLCV failed for {symbol}: {e}")

        logger.error(f"All OHLCV sources failed for {symbol}")
        return None

    # ── Parquet I/O ───────────────────────────────────────────────────────────

    def _get_parquet_path(self, symbol: str, timeframe: str) -> Path:
        """Returns path: data/market_data/ohlcv/{symbol}/{timeframe}.parquet"""
        safe_symbol = symbol.replace("=", "_").replace("/", "_").replace("^", "_")
        path = self._parquet_dir / safe_symbol
        path.mkdir(parents=True, exist_ok=True)
        return path / f"{timeframe}.parquet"

    def _load_parquet(self, symbol: str, timeframe: str = "daily") -> Optional[pd.DataFrame]:
        """Load OHLCV Parquet file for symbol."""
        path = self._get_parquet_path(symbol, timeframe)
        if not path.exists():
            return None
        try:
            df = pd.read_parquet(path)
            if "date" in df.columns:
                df["date"] = pd.to_datetime(df["date"]).dt.date
            df.sort_values("date", inplace=True)
            return df
        except Exception as e:
            logger.error(f"Failed to load Parquet for {symbol}/{timeframe}: {e}")
            return None

    def _update_parquet(self, symbol: str, new_df: pd.DataFrame, timeframe: str = "daily"):
        """
        Append-only Parquet update: read existing → append new → dedup by date → write.
        Per SPEC Section 10.3: Parquet is append-only.
        """
        path = self._get_parquet_path(symbol, timeframe)
        try:
            if path.exists():
                existing = pd.read_parquet(path)
                if "date" in existing.columns:
                    existing["date"] = pd.to_datetime(existing["date"]).dt.date
                combined = pd.concat([existing, new_df], ignore_index=True)
            else:
                combined = new_df.copy()

            if "date" in combined.columns:
                combined["date"] = pd.to_datetime(combined["date"]).dt.date

            # Deduplicate by date, keep last
            combined.drop_duplicates(subset=["date"], keep="last", inplace=True)
            combined.sort_values("date", inplace=True)
            combined.reset_index(drop=True, inplace=True)
            combined.to_parquet(path, index=False, engine="pyarrow")
            logger.debug(f"Parquet updated for {symbol}/{timeframe}: {len(combined)} rows")
        except Exception as e:
            logger.error(f"Failed to update Parquet for {symbol}/{timeframe}: {e}")

    def _is_parquet_fresh(self, df: pd.DataFrame) -> bool:
        """Check if most recent Parquet row is within 2 trading days."""
        if df is None or df.empty or "date" not in df.columns:
            return False
        try:
            last_date = pd.to_datetime(df["date"].max()).date()
            today = datetime.utcnow().date()
            # Data from within 2 calendar days is fresh enough
            return (today - last_date).days <= 2
        except Exception:
            return False

    def _filter_by_days(self, df: pd.DataFrame, days: int) -> pd.DataFrame:
        """Return only rows within the last N days."""
        if df is None or df.empty or "date" not in df.columns:
            return df
        try:
            cutoff = (datetime.utcnow() - timedelta(days=days)).date()
            df["date"] = pd.to_datetime(df["date"]).dt.date
            return df[df["date"] >= cutoff].reset_index(drop=True)
        except Exception:
            return df

    # ── Quote ─────────────────────────────────────────────────────────────────

    def get_quote(self, symbol: str) -> dict:
        """Fetch current market quote. Cache 5 minutes."""
        cache_key = f"quote:{symbol}"
        cached = cache_get(cache_key)
        if cached is not None:
            return cached

        quote = self.yahoo.fetch_quote(symbol)
        cache_set(cache_key, quote, ttl=QUOTE_CACHE_TTL)
        return quote

    # ── Options ───────────────────────────────────────────────────────────────

    def get_options_chain(self, symbol: str) -> tuple:
        """Fetch options chain (calls_df, puts_df). Cache 15 min."""
        cache_key = f"options:{symbol}"
        cached = cache_get(cache_key)
        if cached is not None:
            return cached

        result = self.cboe.fetch_options_chain(symbol)
        cache_set(cache_key, result, ttl=OPTIONS_CACHE_TTL)
        return result

    # ── VIX ───────────────────────────────────────────────────────────────────

    def get_vix_data(self) -> dict:
        """Fetch current VIX data. Cache 15 min."""
        return self.cboe.fetch_vix_data()

    # ── Technical Indicators ──────────────────────────────────────────────────

    def get_indicators(self, symbol: str) -> dict:
        """
        Compute common technical indicators from OHLCV data.
        Returns dict matching MarketIndicatorsResponse schema.
        """
        try:
            df = self.get_ohlcv(symbol, period="1y")
            if df is None or df.empty or len(df) < 20:
                return self._empty_indicators(symbol)

            close = df["close"]
            high = df["high"]
            low = df["low"]
            volume = df["volume"]
            today = df["date"].iloc[-1] if "date" in df.columns else None

            # Simple Moving Averages
            sma_20 = float(close.rolling(20).mean().iloc[-1]) if len(close) >= 20 else None
            sma_50 = float(close.rolling(50).mean().iloc[-1]) if len(close) >= 50 else None
            sma_200 = float(close.rolling(200).mean().iloc[-1]) if len(close) >= 200 else None

            # Exponential Moving Averages
            ema_12 = float(close.ewm(span=12, adjust=False).mean().iloc[-1])
            ema_26 = float(close.ewm(span=26, adjust=False).mean().iloc[-1])

            # RSI 14
            rsi_14 = self._compute_rsi(close, period=14)

            # ADX 14
            adx_14 = self._compute_adx(high, low, close, period=14)

            # ATR 14
            atr_14 = self._compute_atr(high, low, close, period=14)

            # MACD
            macd_line = close.ewm(span=12, adjust=False).mean() - close.ewm(span=26, adjust=False).mean()
            macd_signal = macd_line.ewm(span=9, adjust=False).mean()
            macd = float(macd_line.iloc[-1])
            macd_signal_val = float(macd_signal.iloc[-1])

            # Bollinger Bands
            bb_mid = close.rolling(20).mean()
            bb_std = close.rolling(20).std()
            bb_upper = float((bb_mid + 2 * bb_std).iloc[-1]) if len(close) >= 20 else None
            bb_lower = float((bb_mid - 2 * bb_std).iloc[-1]) if len(close) >= 20 else None

            # Volume SMA 20
            volume_sma_20 = float(volume.rolling(20).mean().iloc[-1]) if len(volume) >= 20 else None

            return {
                "symbol": symbol,
                "date": str(today),
                "sma_20": sma_20,
                "sma_50": sma_50,
                "sma_200": sma_200,
                "ema_12": ema_12,
                "ema_26": ema_26,
                "rsi_14": rsi_14,
                "adx_14": adx_14,
                "atr_14": atr_14,
                "macd": macd,
                "macd_signal": macd_signal_val,
                "bb_upper": bb_upper,
                "bb_lower": bb_lower,
                "volume_sma_20": volume_sma_20,
            }
        except Exception as e:
            logger.error(f"Failed to compute indicators for {symbol}: {e}")
            return self._empty_indicators(symbol)

    def _compute_rsi(self, close: pd.Series, period: int = 14) -> Optional[float]:
        """Compute RSI(period) for a price series."""
        if len(close) < period + 1:
            return None
        try:
            delta = close.diff()
            gain = delta.where(delta > 0, 0.0).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0.0)).rolling(window=period).mean()
            rs = gain / loss.replace(0, np.nan)
            rsi = 100 - (100 / (1 + rs))
            return float(rsi.iloc[-1])
        except Exception:
            return None

    def _compute_atr(self, high: pd.Series, low: pd.Series, close: pd.Series,
                     period: int = 14) -> Optional[float]:
        """Compute Average True Range."""
        if len(close) < period + 1:
            return None
        try:
            prev_close = close.shift(1)
            tr = pd.concat([
                high - low,
                (high - prev_close).abs(),
                (low - prev_close).abs(),
            ], axis=1).max(axis=1)
            atr = tr.rolling(period).mean()
            return float(atr.iloc[-1])
        except Exception:
            return None

    def _compute_adx(self, high: pd.Series, low: pd.Series, close: pd.Series,
                     period: int = 14) -> Optional[float]:
        """Compute ADX(period)."""
        if len(close) < period * 2:
            return None
        try:
            prev_high = high.shift(1)
            prev_low = low.shift(1)
            prev_close = close.shift(1)

            plus_dm = high - prev_high
            minus_dm = prev_low - low
            plus_dm = plus_dm.where((plus_dm > minus_dm) & (plus_dm > 0), 0.0)
            minus_dm = minus_dm.where((minus_dm > plus_dm) & (minus_dm > 0), 0.0)

            tr = pd.concat([
                high - low,
                (high - prev_close).abs(),
                (low - prev_close).abs(),
            ], axis=1).max(axis=1)

            atr = tr.rolling(period).mean()
            plus_di = 100 * (plus_dm.rolling(period).mean() / atr.replace(0, np.nan))
            minus_di = 100 * (minus_dm.rolling(period).mean() / atr.replace(0, np.nan))
            dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, np.nan)
            adx = dx.rolling(period).mean()
            return float(adx.iloc[-1])
        except Exception:
            return None

    def _empty_indicators(self, symbol: str) -> dict:
        return {
            "symbol": symbol, "date": None,
            "sma_20": None, "sma_50": None, "sma_200": None,
            "ema_12": None, "ema_26": None,
            "rsi_14": None, "adx_14": None, "atr_14": None,
            "macd": None, "macd_signal": None,
            "bb_upper": None, "bb_lower": None, "volume_sma_20": None,
        }

    # ── Market Regime (thin wrapper) ──────────────────────────────────────────

    def get_market_regime(self, db=None) -> dict:
        """
        Return current market regime from the most recent Agent 1 output in DB.
        Falls back to a computed regime from SPY if no DB output exists.
        """
        # Try to load latest Agent 1 output from DB
        if db is not None:
            try:
                from modules.agents.models import AgentOutput as AgentOutputModel
                from sqlalchemy import desc
                row = (
                    db.query(AgentOutputModel)
                    .filter_by(agent_id=1, symbol="SPY")
                    .order_by(desc(AgentOutputModel.created_at))
                    .first()
                )
                if row:
                    return {
                        "regime": row.signal,
                        "score": row.score,
                        "source": "agent_1",
                    }
            except Exception:
                pass

        # Fallback: compute from SPY data
        try:
            df = self.get_ohlcv("SPY", period="1y")
            if df is not None and len(df) >= 20:
                adx = self.get_indicators("SPY").get("adx_14", 20)
                regime = "Trending" if adx and adx > 25 else "Range-Bound"
                return {"regime": regime, "score": 50.0, "source": "computed"}
        except Exception:
            pass

        return {"regime": "Unknown", "score": 50.0, "source": "default"}
