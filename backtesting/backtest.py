from data.fetch_data import get_btc_data

from indicators.ema import (
    calculate_ema,
    get_trend
)


def run_backtest():

    btc = get_btc_data()

    close_prices = btc[("Close", "BTC-USD")]

    signals_generated = 0

    for i in range(50, len(close_prices)):

        historical_data = close_prices.iloc[:i]

        ema50 = calculate_ema(
            historical_data,
            50
        )

        latest_price = historical_data.iloc[-1]

        latest_ema50 = ema50.iloc[-1]

        if latest_price > latest_ema50:
            signal = "BUY"
        else:
            signal = "SELL"

        print(
            historical_data.index[-1].date(),
            signal
        )

        signals_generated += 1

    print()
    print("Signals Generated:", signals_generated)


if __name__ == "__main__":
    run_backtest()