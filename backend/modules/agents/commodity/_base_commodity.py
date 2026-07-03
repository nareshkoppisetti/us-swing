"""Shared base logic for commodity agents 35-42."""
import numpy as np
from modules.agents.base_agent import Signal

def commodity_score(close_series, inv_change=0, inv_weight=0.5):
    import pandas as pd
    close = pd.Series(close_series).astype(float)
    if len(close) < 20: return 50.0, Signal.NEUTRAL
    price = float(close.iloc[-1])
    sma20 = float(close.rolling(20).mean().iloc[-1])
    ret_1m = (price / float(close.iloc[-21]) - 1) * 100 if len(close) > 21 else 0
    score = 50 + (price / sma20 - 1) * 200 + ret_1m * 2 - float(inv_change or 0) * inv_weight
    score = float(np.clip(score, 0, 100))
    signal = Signal.BULLISH if score >= 58 else (Signal.BEARISH if score <= 42 else Signal.NEUTRAL)
    return score, signal
