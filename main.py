from data.fetch_data import get_btc_data
from indicators.ema import calculate_ema
from indicators.ema import get_trend


btc = get_btc_data()

close_prices = btc[("Close", "BTC-USD")]

ema50 = calculate_ema(close_prices, 50)

ema200 = calculate_ema(close_prices, 200)

latest_ema50 = ema50.iloc[-1]
latest_ema200 = ema200.iloc[-1]

trend = get_trend(
    latest_ema50,
    latest_ema200
)

print("=" * 40)
print("TradeSense AI")
print("=" * 40)

print()

print("EMA50:", round(latest_ema50, 2))
print("EMA200:", round(latest_ema200, 2))

print()

print("Trend:", trend)

