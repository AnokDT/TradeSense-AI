from data.fetch_data import get_btc_data

from indicators.ema import (
    calculate_ema
)


def run_backtest():

    btc = get_btc_data()

    close_prices = btc[("Close", "BTC-USD")]

    position = None
    buy_price = 0

    trades = 0

    print("=" * 50)
    print("TradeSense Backtest")
    print("=" * 50)
    print()

    for i in range(50, len(close_prices)):

        historical_data = close_prices.iloc[:i]

        ema50 = calculate_ema(
            historical_data,
            50
        )

        current_price = historical_data.iloc[-1]

        current_date = historical_data.index[-1].date()

        current_ema50 = ema50.iloc[-1]

        signal = "BUY" if current_price > current_ema50 else "SELL"

        # ENTER TRADE

        if signal == "BUY" and position is None:

            position = "LONG"
            buy_price = current_price

            print(
                f"{current_date} | BUY @ ${buy_price:.2f}"
            )

        # EXIT TRADE

        elif signal == "SELL" and position == "LONG":

            sell_price = current_price

            profit_pct = (
                (sell_price - buy_price)
                / buy_price
            ) * 100

            trades += 1

            print(
                f"{current_date} | SELL @ ${sell_price:.2f}"
            )

            print(
                f"Trade #{trades} Profit: "
                f"{profit_pct:.2f}%"
            )

            print()

            position = None

    print("=" * 50)
    print("Backtest Complete")
    print("=" * 50)

    print()

    print("Trades Closed:", trades)


if __name__ == "__main__":
    run_backtest()