def calculate_ema(series, period):
    return series.ewm(span=period).mean()


def get_trend(ema50, ema200):
    if ema50 > ema200:
        return "bullish"

    elif ema50 < ema200:
        return "bearish"

    return "neutral"