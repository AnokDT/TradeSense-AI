def calculate_score(trend, rsi_signal):

    bull_score = 0
    bear_score = 0

    if trend == "bullish":
        bull_score += 50

    elif trend == "bearish":
        bear_score += 50

    if rsi_signal == "bullish":
        bull_score += 50

    elif rsi_signal == "bearish":
        bear_score += 50

    return bull_score, bear_score