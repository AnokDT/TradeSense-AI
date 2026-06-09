def get_trend(ema50, ema200):
    if ema50 > ema200:
        return "bullish"
    elif ema50 < ema200:
        return "bearish"
    else:
        return "neutral"