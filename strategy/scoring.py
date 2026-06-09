def calculate_score(trend, rsi_signal):

    bull_score = 0
    bear_score = 0

    # EMA Trend

    if trend == "bullish":
        bull_score += 60

    elif trend == "bearish":
        bear_score += 60

    # RSI

    if rsi_signal == "bullish":
        bull_score += 20

    elif rsi_signal == "bearish":
        bear_score += 20

    elif rsi_signal == "overbought":
        bear_score += 40

    elif rsi_signal == "oversold":
        bull_score += 40

    return bull_score, bear_score