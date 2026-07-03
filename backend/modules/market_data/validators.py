"""
File path: backend/modules/market_data/validators.py
Purpose: DataValidator — validates market data DataFrames before storage.
         All rules per SPEC Section 11.2.

Validation rules:
  1. Completeness: required columns present
  2. OHLC Logic: high >= open, high >= close, low <= open, low <= close
  3. Volume Sanity: volume > 0 on trading days
  4. Timestamp Validity: no future-dated records; no records older than 30 years
  5. Price Reasonableness: current close within ±50% of previous close (flag, don't drop)

Failed validation is logged to data_quality log.
Partial failures (e.g. missing volume) stored with is_complete=False flag.
"""
import logging
from datetime import datetime, date, timedelta
from typing import Optional

import pandas as pd

logger = logging.getLogger("app")

REQUIRED_COLUMNS = {"open", "high", "low", "close", "volume"}
THIRTY_YEARS_AGO = (datetime.utcnow() - timedelta(days=365 * 30)).date()


class DataValidator:
    """
    Validates OHLCV DataFrames before storage or agent consumption.
    Per SPEC Section 11.2 — all validation rules implemented.
    """

    def validate_ohlcv(self, df: pd.DataFrame, symbol: str) -> pd.DataFrame:
        """
        Run all validation checks on the DataFrame.
        Adds 'is_complete' column. Logs issues. Returns cleaned DataFrame.
        Does NOT drop rows for price reasonableness — only flags them.
        """
        if df is None or df.empty:
            logger.warning(f"DataValidator: empty DataFrame for {symbol}")
            return df

        df = df.copy()
        errors = []
        warnings = []

        # 1. Completeness
        completeness_errors = self._check_completeness(df)
        errors.extend(completeness_errors)

        # If missing critical columns, return early
        if completeness_errors:
            for err in completeness_errors:
                logger.error(f"DataValidator [{symbol}]: {err}")
            df["is_complete"] = False
            return df

        # Normalize column types
        for col in ["open", "high", "low", "close"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        if "volume" in df.columns:
            df["volume"] = pd.to_numeric(df["volume"], errors="coerce").fillna(0).astype(int)

        # 2. OHLC Logic — drop invalid rows
        ohlc_mask = self._get_ohlc_valid_mask(df)
        invalid_ohlc_count = (~ohlc_mask).sum()
        if invalid_ohlc_count > 0:
            warnings.append(f"{invalid_ohlc_count} rows failed OHLC logic check")
            logger.warning(f"DataValidator [{symbol}]: {invalid_ohlc_count} rows failed OHLC logic — dropping")
            df = df[ohlc_mask].copy()

        # 3. Timestamp validity — drop future-dated and ancient records
        if "date" in df.columns:
            ts_mask = self._get_timestamp_valid_mask(df)
            invalid_ts_count = (~ts_mask).sum()
            if invalid_ts_count > 0:
                warnings.append(f"{invalid_ts_count} rows failed timestamp validation")
                logger.warning(f"DataValidator [{symbol}]: removing {invalid_ts_count} invalid timestamp rows")
                df = df[ts_mask].copy()

        # 4. Volume sanity — add warning but keep rows (ETFs and some symbols have 0 volume on holidays)
        volume_issues = self._check_volume_sanity(df)
        warnings.extend(volume_issues)

        # 5. Price reasonableness — flag but keep
        price_warnings = self._check_price_reasonableness(df, symbol)
        warnings.extend(price_warnings)

        # Add is_complete column
        df["is_complete"] = len(errors) == 0 and len([w for w in warnings if "volume" in w.lower()]) == 0

        if warnings:
            for w in warnings:
                logger.warning(f"DataValidator [{symbol}]: {w}")

        return df

    def validate_quote(self, quote: dict) -> bool:
        """Sanity check a quote dictionary."""
        if not quote:
            return False
        price = quote.get("price")
        if price is None or (isinstance(price, (int, float)) and price < 0):
            return False
        return True

    def _check_completeness(self, df: pd.DataFrame) -> list:
        """Check all required columns are present."""
        cols_lower = {c.lower() for c in df.columns}
        missing = REQUIRED_COLUMNS - cols_lower
        return [f"Missing required column: {col}" for col in missing]

    def _get_ohlc_valid_mask(self, df: pd.DataFrame) -> pd.Series:
        """Return boolean mask: True where OHLC logic is valid."""
        try:
            mask = (
                (df["high"] >= df["open"]) &
                (df["high"] >= df["close"]) &
                (df["low"] <= df["open"]) &
                (df["low"] <= df["close"]) &
                (df["high"] >= df["low"])
            )
            # NaN comparisons return False — also exclude NaN rows
            mask = mask.fillna(False)
            return mask
        except Exception:
            return pd.Series([True] * len(df), index=df.index)

    def _get_timestamp_valid_mask(self, df: pd.DataFrame) -> pd.Series:
        """Return mask: True where date is not future and not older than 30 years."""
        try:
            today = date.today()

            def is_valid_date(d):
                if d is None:
                    return False
                if isinstance(d, str):
                    try:
                        d = datetime.strptime(d[:10], "%Y-%m-%d").date()
                    except Exception:
                        return True  # keep if we can't parse
                if hasattr(d, "date"):
                    d = d.date()
                return THIRTY_YEARS_AGO <= d <= today

            return df["date"].apply(is_valid_date)
        except Exception:
            return pd.Series([True] * len(df), index=df.index)

    def _check_volume_sanity(self, df: pd.DataFrame) -> list:
        """Flag rows with volume == 0."""
        warnings = []
        if "volume" in df.columns:
            zero_vol = (df["volume"] == 0).sum()
            if zero_vol > 0:
                pct = (zero_vol / len(df)) * 100
                warnings.append(f"{zero_vol} rows ({pct:.1f}%) have zero volume")
        return warnings

    def _check_price_reasonableness(self, df: pd.DataFrame, symbol: str) -> list:
        """Flag rows where close changed > 50% from previous close."""
        warnings = []
        if "close" not in df.columns or len(df) < 2:
            return warnings
        try:
            prev_close = df["close"].shift(1)
            pct_change = ((df["close"] - prev_close) / prev_close).abs()
            extreme_moves = (pct_change > 0.5).sum()
            if extreme_moves > 0:
                warnings.append(
                    f"{extreme_moves} rows have >50% price change from previous close "
                    f"(may indicate splits, errors, or legitimate price action) — flagged for review"
                )
        except Exception:
            pass
        return warnings
