def get_reasons(
    trend,
    rsi_signal,
    volume_signal
):

    reasons = []

    if trend == "bullish":
        reasons.append(
            "EMA50 is above EMA200"
        )

    elif trend == "bearish":
        reasons.append(
            "EMA50 is below EMA200"
        )

    if rsi_signal == "oversold":
        reasons.append(
            "RSI shows extreme oversold conditions"
        )

    elif rsi_signal == "overbought":
        reasons.append(
            "RSI shows overbought conditions"
        )

    if volume_signal == "high":
        reasons.append(
            "Trading volume is above average"
        )

    return reasons