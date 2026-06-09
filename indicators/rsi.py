def get_rsi_signal(rsi):
    if rsi > 60:
        return "bullish"
    elif rsi < 40:
        return "bearish"
    else:
        return "neutral"