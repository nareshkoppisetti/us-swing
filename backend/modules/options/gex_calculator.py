"""
File path: backend/modules/options/gex_calculator.py
Purpose: GEXCalculator — standalone Gamma Exposure calculation engine.
         Used by Agent 22 (Gamma Exposure) and OptionsIntelligenceService.
         Per SPEC Agent 22 data requirements.

GEX Formula (per SPEC):
  GEX_per_contract = OI × gamma × contract_size × spot_price²  / 100
  Dealer GEX = sum(call GEX) - sum(put GEX)   # dealers are short calls, long puts
  Total GEX = sum across all strikes and expiries
  Gamma Flip = strike where cumulative GEX changes sign

Interpretation:
  Positive Total GEX → dealers long gamma → stabilizing (sell rips, buy dips)
  Negative Total GEX → dealers short gamma → destabilizing (chase moves)
  Gamma Flip = key support/resistance level where dealer behavior switches

Contract size: 100 shares per options contract.

NOTE ON GREEKS: Yahoo Finance's options chain does not include gamma directly,
so gamma is computed here via the standard Black-Scholes formula from each
contract's strike, days-to-expiry, implied volatility, and the underlying
spot price. Risk-free rate is approximated at 4.5% (roughly current T-bill
yield) since we don't have a live rate feed wired to this module.
"""
import logging
import math
from datetime import date, datetime

logger = logging.getLogger("app")

CONTRACT_SIZE = 100
RISK_FREE_RATE = 0.045  # approximate — see note above


def _norm_pdf(x: float) -> float:
    return math.exp(-0.5 * x * x) / math.sqrt(2 * math.pi)


def black_scholes_gamma(spot: float, strike: float, days_to_expiry: float,
                         iv: float, r: float = RISK_FREE_RATE) -> float:
    """
    Black-Scholes gamma — identical formula for calls and puts.
    Returns 0.0 for degenerate inputs (expired, zero IV, etc.) rather than raising,
    since a single bad contract shouldn't blow up an entire chain calculation.
    """
    try:
        t = max(days_to_expiry, 0) / 365.0
        if t <= 0 or iv is None or iv <= 0 or spot <= 0 or strike <= 0:
            return 0.0
        d1 = (math.log(spot / strike) + (r + 0.5 * iv ** 2) * t) / (iv * math.sqrt(t))
        return _norm_pdf(d1) / (spot * iv * math.sqrt(t))
    except (ValueError, ZeroDivisionError):
        return 0.0


class GEXCalculator:
    """Computes dealer Gamma Exposure from an options chain DataFrame."""

    def compute(self, options_df, spot_price: float) -> dict:
        """
        Compute GEX for all strikes from options chain data.

        Args:
            options_df: DataFrame with columns:
                        strike, option_type (call/put), open_interest,
                        gamma (optional — computed via Black-Scholes if absent),
                        expiry_date, implied_volatility (needed if gamma absent)
            spot_price: Current underlying price

        Returns dict with total_gex, by_strike, gamma_flip_level, is_positive,
        top_call_strikes, top_put_strikes.
        """
        if options_df is None or options_df.empty or spot_price <= 0:
            return {
                "total_gex": 0.0, "by_strike": {}, "gamma_flip_level": None,
                "is_positive": None, "top_call_strikes": [], "top_put_strikes": [],
            }

        by_strike = {}
        call_contributions = {}
        put_contributions = {}

        for _, row in options_df.iterrows():
            strike = float(row.get("strike", 0) or 0)
            oi = float(row.get("open_interest", 0) or 0)
            opt_type = str(row.get("option_type", "")).lower()
            if strike <= 0 or oi <= 0 or opt_type not in ("call", "put"):
                continue

            gamma = row.get("gamma")
            if gamma is None or (isinstance(gamma, float) and math.isnan(gamma)):
                expiry = row.get("expiry_date")
                dte = self._days_to_expiry(expiry)
                iv = float(row.get("implied_volatility", 0) or 0)
                gamma = black_scholes_gamma(spot_price, strike, dte, iv)
            else:
                gamma = float(gamma)

            gex = oi * gamma * CONTRACT_SIZE * (spot_price ** 2) / 100.0
            if opt_type == "put":
                gex = -gex
                put_contributions[strike] = put_contributions.get(strike, 0.0) + gex
            else:
                call_contributions[strike] = call_contributions.get(strike, 0.0) + gex

            by_strike[strike] = by_strike.get(strike, 0.0) + gex

        total_gex = sum(by_strike.values())
        gamma_flip = self.find_gamma_flip(by_strike)

        top_call_strikes = sorted(call_contributions.items(), key=lambda kv: kv[1], reverse=True)[:5]
        top_put_strikes = sorted(put_contributions.items(), key=lambda kv: kv[1])[:5]

        return {
            "total_gex": total_gex,
            "by_strike": {str(k): v for k, v in sorted(by_strike.items())},
            "gamma_flip_level": gamma_flip,
            "is_positive": total_gex > 0,
            "top_call_strikes": [{"strike": s, "gex": v} for s, v in top_call_strikes],
            "top_put_strikes": [{"strike": s, "gex": v} for s, v in top_put_strikes],
        }

    def find_gamma_flip(self, by_strike: dict):
        """Find the strike price where cumulative GEX changes sign."""
        if not by_strike:
            return None
        strikes = sorted(by_strike.keys())
        cumulative = 0.0
        prev_strike, prev_cum = None, None
        for strike in strikes:
            cumulative += by_strike[strike]
            if prev_cum is not None and (prev_cum < 0) != (cumulative < 0):
                # Sign changed between prev_strike and strike — interpolate
                return round((prev_strike + strike) / 2, 2)
            prev_strike, prev_cum = strike, cumulative
        return None

    def get_call_wall(self, by_strike: dict):
        """Return the strike with the highest (most positive) GEX — resistance."""
        if not by_strike:
            return None
        return max(by_strike.items(), key=lambda kv: kv[1])[0]

    def get_put_wall(self, by_strike: dict):
        """Return the strike with the most negative GEX — support."""
        if not by_strike:
            return None
        return min(by_strike.items(), key=lambda kv: kv[1])[0]

    @staticmethod
    def _days_to_expiry(expiry) -> float:
        try:
            if isinstance(expiry, str):
                expiry = datetime.strptime(expiry, "%Y-%m-%d").date()
            if isinstance(expiry, datetime):
                expiry = expiry.date()
            if isinstance(expiry, date):
                return max((expiry - date.today()).days, 0)
        except Exception:
            pass
        return 0.0
