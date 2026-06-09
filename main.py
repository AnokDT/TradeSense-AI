from indicators.ema import get_trend
from indicators.rsi import get_rsi_signal

from strategy.scoring import calculate_score


ema50 = 65000
ema200 = 62000

rsi = 65


trend = get_trend(ema50, ema200)

rsi_signal = get_rsi_signal(rsi)

bull_score, bear_score = calculate_score(
    trend,
    rsi_signal
)

print("=" * 40)
print("TradeSense AI")
print("=" * 40)

print("Trend:", trend)
print("RSI Signal:", rsi_signal)

print()
print("Bull Score:", bull_score)
print("Bear Score:", bear_score)

if bull_score > bear_score:
    print("Action: BUY")

elif bear_score > bull_score:
    print("Action: SELL")

else:
    print("Action: WAIT")