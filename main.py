# =========================
# TradeSense AI
# Main Program
# =========================

# ----- Imports -----

from data.fetch_data import get_btc_data

from indicators.ema import (
    calculate_ema,
    get_trend
)

from indicators.rsi import (
    calculate_rsi,
    get_rsi_signal
)

from strategy.scoring import calculate_score


# =========================
# 1. FETCH MARKET DATA
# =========================

btc = get_btc_data()

close_prices = btc[("Close", "BTC-USD")]


# =========================
# 2. CALCULATE EMA
# =========================

ema50 = calculate_ema(close_prices, 50)
ema200 = calculate_ema(close_prices, 200)

latest_ema50 = ema50.iloc[-1]
latest_ema200 = ema200.iloc[-1]

trend = get_trend(
    latest_ema50,
    latest_ema200
)


# =========================
# 3. CALCULATE RSI
# =========================

rsi = calculate_rsi(close_prices)

latest_rsi = rsi.iloc[-1]

rsi_signal = get_rsi_signal(
    latest_rsi
)


# =========================
# 4. CALCULATE SCORES
# =========================

bull_score, bear_score = calculate_score(
    trend,
    rsi_signal
)


# =========================
# 5. DETERMINE ACTION
# =========================

if bull_score > bear_score:
    action = "BUY"

elif bear_score > bull_score:
    action = "SELL"

else:
    action = "WAIT"


# =========================
# 6. CALCULATE CONFIDENCE
# =========================

total_score = bull_score + bear_score

if total_score > 0:
    confidence = round(
        max(bull_score, bear_score) / total_score * 100,
        1
    )
else:
    confidence = 50


# =========================
# 7. SIGNAL STRENGTH
# =========================

if confidence >= 85:
    strength = "Very Strong"

elif confidence >= 70:
    strength = "Strong"

elif confidence >= 60:
    strength = "Moderate"

else:
    strength = "Weak"


# =========================
# 6. DISPLAY RESULTS
# =========================

print("=" * 40)
print("TradeSense AI")
print("=" * 40)

print()

print("Current Price:", round(close_prices.iloc[-1], 2))

print()

print("EMA50:", round(latest_ema50, 2))
print("EMA200:", round(latest_ema200, 2))

print()

print("Trend:", trend)

print()

print("RSI:", round(latest_rsi, 2))
print("RSI Signal:", rsi_signal)

print()

print("Bull Score:", bull_score)
print("Bear Score:", bear_score)

print()

print("Action:", action)
print("Confidence:", confidence, "%")

if confidence >= 85:
    print("Signal Strength: VERY STRONG")

elif confidence >= 70:
    print("Signal Strength: STRONG")

elif confidence >= 60:
    print("Signal Strength: MODERATE")

else:
    print("Signal Strength: WEAK")

print()
print("=" * 40)