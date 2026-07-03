"""
File path: backend/modules/options/service.py
Purpose: OptionsIntelligenceService — fetches and analyzes options chain data.
Per SPEC Agents 21, 22, 24, 34 data requirements and API.md "Options Intelligence".
"""
import logging
from datetime import datetime

import pandas as pd
from sqlalchemy.orm import Session

from core.exceptions import DataUnavailableError
from modules.options.gex_calculator import GEXCalculator
from modules.market_data.collectors.cboe_collector import CBOECollector

logger = logging.getLogger("app")


def _normalize_chain(calls_df: pd.DataFrame, puts_df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize yfinance's raw call/put DataFrames into a single frame with the
    column names our internal formulas expect: strike, option_type,
    open_interest, implied_volatility, expiry_date.
    """
    frames = []
    for df, opt_type in [(calls_df, "call"), (puts_df, "put")]:
        if df is None or df.empty:
            continue
        d = df.copy()
        d["option_type"] = opt_type
        d.rename(columns={
            "openInterest": "open_interest",
            "impliedVolatility": "implied_volatility",
            "expiration": "expiry_date",
            "lastPrice": "last_price",
        }, inplace=True)
        frames.append(d)
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)


class OptionsIntelligenceService:
    def __init__(self, db: Session, cache=None):
        self.db = db
        self.cache = cache
        self._cboe = CBOECollector()
        self._gex = GEXCalculator()

    def fetch_options_chain(self, symbol: str) -> list:
        """Fetch full options chain (all expiries, all strikes) for symbol."""
        from modules.market_data.service import MarketDataService
        calls_df, puts_df = MarketDataService().get_options_chain(symbol)
        chain = _normalize_chain(calls_df, puts_df)
        if chain.empty:
            raise DataUnavailableError(f"No options chain available for {symbol}")

        rows = []
        for _, r in chain.iterrows():
            rows.append({
                "expiry_date": str(r.get("expiry_date", "")),
                "strike": float(r.get("strike", 0) or 0),
                "option_type": r.get("option_type"),
                "bid": float(r["bid"]) if pd.notna(r.get("bid")) else None,
                "ask": float(r["ask"]) if pd.notna(r.get("ask")) else None,
                "volume": int(r["volume"]) if pd.notna(r.get("volume")) else None,
                "open_interest": int(r["open_interest"]) if pd.notna(r.get("open_interest")) else None,
                "implied_volatility": float(r["implied_volatility"]) if pd.notna(r.get("implied_volatility")) else None,
            })
        return rows

    def compute_put_call_ratio(self, symbol: str) -> float:
        """Compute put/call OI ratio across near-term expiries."""
        from modules.market_data.service import MarketDataService
        calls_df, puts_df = MarketDataService().get_options_chain(symbol)
        call_oi = float(calls_df["openInterest"].fillna(0).sum()) if calls_df is not None and not calls_df.empty and "openInterest" in calls_df.columns else 0.0
        put_oi = float(puts_df["openInterest"].fillna(0).sum()) if puts_df is not None and not puts_df.empty and "openInterest" in puts_df.columns else 0.0
        if call_oi == 0:
            raise DataUnavailableError(f"No call open interest for {symbol} — cannot compute put/call ratio")
        return round(put_oi / call_oi, 4)

    def compute_gamma_exposure(self, symbol: str) -> dict:
        """Compute dealer Gamma Exposure (GEX) by strike, using Black-Scholes gamma."""
        from modules.market_data.service import MarketDataService
        svc = MarketDataService()
        calls_df, puts_df = svc.get_options_chain(symbol)
        chain = _normalize_chain(calls_df, puts_df)
        if chain.empty:
            raise DataUnavailableError(f"No options chain available for {symbol}")

        quote = svc.get_quote(symbol)
        spot = float(quote.get("price") or 0)
        if spot <= 0:
            raise DataUnavailableError(f"No spot price available for {symbol}")

        result = self._gex.compute(chain, spot)
        result["symbol"] = symbol
        result["snapshot_at"] = datetime.utcnow().isoformat()
        return result

    def compute_max_pain(self, symbol: str, expiry: str) -> float:
        """
        Max pain: the strike price at which option WRITERS (sellers) lose the
        least money in aggregate — i.e. where total intrinsic value paid out
        to holders is minimized. Computed by testing every strike as the
        hypothetical settlement price.
        """
        from modules.market_data.service import MarketDataService
        calls_df, puts_df = MarketDataService().get_options_chain(symbol)
        chain = _normalize_chain(calls_df, puts_df)
        if chain.empty:
            raise DataUnavailableError(f"No options chain available for {symbol}")

        if expiry:
            chain = chain[chain["expiry_date"].astype(str) == str(expiry)]
        if chain.empty:
            raise DataUnavailableError(f"No options for {symbol} expiring {expiry}")

        strikes = sorted(chain["strike"].dropna().unique())
        if not strikes:
            raise DataUnavailableError(f"No strikes found for {symbol} {expiry}")

        best_strike, min_pain = strikes[0], float("inf")
        for hypothetical_price in strikes:
            pain = 0.0
            for _, row in chain.iterrows():
                strike = float(row["strike"])
                oi = float(row.get("open_interest", 0) or 0)
                if row["option_type"] == "call" and hypothetical_price > strike:
                    pain += (hypothetical_price - strike) * oi
                elif row["option_type"] == "put" and hypothetical_price < strike:
                    pain += (strike - hypothetical_price) * oi
            if pain < min_pain:
                min_pain, best_strike = pain, hypothetical_price

        return float(best_strike)

    def get_vix_term_structure(self) -> dict:
        """Fetch VIX9D, VIX spot, VIX3M, VIX6M and determine term structure shape."""
        data = self._cboe.fetch_vix_data()
        return {
            "snapshot_at": datetime.utcnow().isoformat(),
            "vix_9d": data.get("vix9d"),
            "vix_spot": data.get("vix"),
            "vix_3m": data.get("vix3m"),
            "vix_6m": data.get("vix6m"),
            "term_structure": data.get("term_structure"),
        }

    def get_iv_skew(self, symbol: str, expiry: str) -> dict:
        """Return {strike: implied_volatility} for calls at a given expiry (IV skew curve)."""
        from modules.market_data.service import MarketDataService
        calls_df, _ = MarketDataService().get_options_chain(symbol)
        if calls_df is None or calls_df.empty:
            raise DataUnavailableError(f"No options chain available for {symbol}")
        d = calls_df.copy()
        if "expiration" in d.columns and expiry:
            d = d[d["expiration"].astype(str) == str(expiry)]
        if d.empty or "impliedVolatility" not in d.columns:
            return {}
        d = d.sort_values("strike")
        return {str(row["strike"]): float(row["impliedVolatility"]) for _, row in d.iterrows() if pd.notna(row.get("impliedVolatility"))}
