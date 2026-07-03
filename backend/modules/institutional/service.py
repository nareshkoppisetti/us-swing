"""
File path: backend/modules/institutional/service.py
Purpose: InstitutionalFlowService — fetches, processes, and stores institutional data.
Orchestrates: dark pool flow, 13F filings, insider transactions, ETF flows.
Per SPEC Agents 15-20 data requirements and API.md "Institutional Flows".
"""
import logging
from datetime import date, datetime, timedelta

import numpy as np
from sqlalchemy.orm import Session

from modules.institutional.models import (
    DarkPoolActivity, InsiderTransaction, ThirteenFHolding,
)

logger = logging.getLogger("app")

# Same sector-ETF mapping Agent 20 already uses, kept in sync here.
RELATED_ETFS = {
    "XLK": ["AAPL", "MSFT", "NVDA", "META", "GOOGL"],
    "XLF": ["JPM", "BAC", "GS", "MS"],
    "XLE": ["XOM", "CVX", "SLB"],
    "XLV": ["UNH", "JNJ", "PFE"],
    "XLI": ["GE", "HON", "MMM"],
}


class InstitutionalFlowService:
    def __init__(self, db: Session, cache=None):
        self.db = db
        self.cache = cache

    # ── Dark Pool ────────────────────────────────────────────────────────────
    def get_dark_pool_activity(self, symbol: str, weeks: int = 4) -> dict:
        """
        FINRA only provides aggregate-only weekly data in MVP mode (per the
        collector's own docstring) — there is no real per-symbol history to
        query from the DB, so we always return the live degraded snapshot.
        """
        from modules.market_data.collectors.finra_ats_collector import FINRAATSCollector
        data = FINRAATSCollector().fetch_ats_volume(symbol)
        return {
            "symbol": symbol,
            "weeks_requested": weeks,
            "is_degraded": data.get("is_degraded", True),
            "weekly_volume": data.get("weekly_volume"),
            "avg_volume_4w": data.get("avg_volume_4w"),
            "volume_ratio": data.get("volume_ratio"),
            "accumulation_score": data.get("accumulation_score"),
            "distribution_score": data.get("distribution_score"),
            "note": data.get("note"),
        }

    # ── 13F ──────────────────────────────────────────────────────────────────
    def get_thirteen_f_holdings(self, symbol: str, quarters: int = 4) -> list:
        """Fetch 13F institutional holdings, DB cache-first with SEC EDGAR fallback."""
        cutoff = date.today() - timedelta(days=quarters * 91)
        rows = (
            self.db.query(ThirteenFHolding)
            .filter(ThirteenFHolding.symbol == symbol, ThirteenFHolding.quarter_end >= cutoff)
            .order_by(ThirteenFHolding.quarter_end.desc())
            .all()
        )
        if rows:
            return [self._13f_out(r) for r in rows]

        from modules.market_data.collectors.sec_edgar_collector import SECEdgarCollector
        holdings = SECEdgarCollector().fetch_13f(symbol)
        results = []
        for h in holdings:
            quarter_str = h.get("quarter") or ""
            try:
                quarter_end = datetime.strptime(quarter_str, "%Y-%m-%d").date() if quarter_str else date.today()
            except ValueError:
                quarter_end = date.today()
            row = ThirteenFHolding(
                symbol=symbol,
                institution_name=h.get("institution_name", "Unknown Institution"),
                quarter_end=quarter_end,
                shares_held=h.get("shares") or None,
                market_value_usd=h.get("value") or None,
                pct_of_portfolio=None,
                change_from_prior=None,
            )
            self.db.add(row)
            results.append(row)
        if results:
            self.db.commit()
        return [self._13f_out(r) for r in results]

    @staticmethod
    def _13f_out(r: ThirteenFHolding) -> dict:
        return {
            "id": r.id, "symbol": r.symbol, "institution_name": r.institution_name,
            "quarter_end": r.quarter_end, "shares_held": r.shares_held,
            "market_value_usd": r.market_value_usd, "pct_of_portfolio": r.pct_of_portfolio,
            "change_from_prior": r.change_from_prior,
        }

    # ── Insider Transactions ────────────────────────────────────────────────
    def get_insider_transactions(self, symbol: str, days: int = 90) -> list:
        """Fetch insider buy/sell transactions, DB cache-first with SEC EDGAR fallback."""
        cutoff = date.today() - timedelta(days=days)
        rows = (
            self.db.query(InsiderTransaction)
            .filter(InsiderTransaction.symbol == symbol, InsiderTransaction.transaction_date >= cutoff)
            .order_by(InsiderTransaction.transaction_date.desc())
            .all()
        )
        if rows:
            return [self._insider_out(r) for r in rows]

        from modules.market_data.collectors.sec_edgar_collector import SECEdgarCollector
        txns = SECEdgarCollector().fetch_form4(symbol, days=days)
        results = []
        for t in txns:
            date_str = t.get("date") or t.get("filing_date") or ""
            try:
                txn_date = datetime.strptime(date_str, "%Y-%m-%d").date() if date_str else date.today()
            except ValueError:
                txn_date = date.today()
            shares = t.get("shares") or 0
            price = t.get("price") or 0.0
            row = InsiderTransaction(
                symbol=symbol,
                transaction_date=txn_date,
                insider_name=t.get("insider_name"),
                insider_role=None,
                transaction_type="P" if str(t.get("transaction_type", "")).lower().startswith("p") else "S",
                shares=shares,
                price_per_share=price,
                total_value=shares * price if shares and price else None,
                form4_url=t.get("url"),
            )
            self.db.add(row)
            results.append(row)
        if results:
            self.db.commit()
        return [self._insider_out(r) for r in results]

    @staticmethod
    def _insider_out(r: InsiderTransaction) -> dict:
        return {
            "id": r.id, "symbol": r.symbol, "transaction_date": r.transaction_date,
            "insider_name": r.insider_name, "insider_role": r.insider_role,
            "transaction_type": r.transaction_type, "shares": r.shares,
            "price_per_share": r.price_per_share, "total_value": r.total_value,
        }

    # ── ETF Flows ────────────────────────────────────────────────────────────
    def get_etf_flow_summary(self, symbol: str) -> dict:
        """
        Estimate ETF flow for symbol from volume/price action in its related
        sector ETF(s) — same AUM-proxy approach as Agent 20.
        """
        from modules.market_data.service import MarketDataService
        svc = MarketDataService()

        sector_etf = next((etf for etf, syms in RELATED_ETFS.items() if symbol in syms), None)
        etfs_to_check = [sector_etf] if sector_etf else list(RELATED_ETFS.keys())[:3]

        results = []
        for etf in etfs_to_check:
            try:
                df = svc.get_ohlcv(etf, period="1mo")
                if df is None or len(df) < 5:
                    continue
                vol = df["volume"].astype(float)
                close = df["close"].astype(float)
                avg_vol = float(vol.rolling(min(10, len(vol))).mean().iloc[-1])
                today_vol = float(vol.iloc[-1])
                vol_ratio = today_vol / avg_vol if avg_vol > 0 else 1.0
                ret_5d = (float(close.iloc[-1]) / float(close.iloc[-6]) - 1) * 100 if len(close) > 5 else 0.0
                results.append({
                    "etf": etf, "volume_ratio": round(vol_ratio, 3),
                    "return_5d_pct": round(ret_5d, 2),
                    "inferred_flow": "inflow" if ret_5d > 0 and vol_ratio > 1 else
                                      "outflow" if ret_5d < 0 and vol_ratio > 1 else "neutral",
                })
            except Exception as e:
                logger.warning(f"ETF flow check failed for {etf}: {e}")

        return {
            "symbol": symbol,
            "related_etfs": results,
            "note": "Flow direction inferred from ETF price/volume action (AUM-flow proxy), not direct fund-flow data.",
        }
