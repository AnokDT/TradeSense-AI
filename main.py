from data.fetch_data import get_btc_data
from indicators.ema import calculate_ema
from indicators.ema import get_trend
from indicators.rsi import calculate_rsi
from indicators.rsi import get_rsi_signal


btc = get_btc_data()

close_prices = btc[("Close", "BTC-USD")]

ema50 = calculate_ema(close_prices, 50)

ema200 = calculate_ema(close_prices, 200)

latest_ema50 = ema50.iloc[-1]
latest_ema200 = ema200.iloc[-1]
rsi = calculate_rsi(close_prices)

latest_rsi = rsi.iloc[-1]

rsi_signal = get_rsi_signal(latest_rsi)

trend = get_trend(
    latest_ema50,
    latest_ema200
)

#PRINTING CODEE :)

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