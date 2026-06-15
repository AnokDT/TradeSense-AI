import pandas as pd
from data.fetch_data import get_btc_data
from strategy.base import BaseStrategy
from strategy.ema_price_crossover import EMAPriceCrossoverStrategy

def run_backtest(strategy: BaseStrategy = None, starting_capital: float = 10000.0, legacy_mode: bool = True, verbose: bool = True):
    """
    Runs a historical backtest of the specified strategy.
    
    Parameters:
    - strategy: An instance of BaseStrategy (defaults to EMAPriceCrossoverStrategy(50))
    - starting_capital: The starting capital for the portfolio (default: 10000.0)
    - legacy_mode: If True, matches the off-by-one indexing of the original version for exact comparison.
    - verbose: If True, prints detailed log of trades and summary stats.
    """
    if strategy is None:
        strategy = EMAPriceCrossoverStrategy(50)

    # Fetch BTC data
    btc = get_btc_data()
    
    # Prepare indicators using the strategy
    prepared_df = strategy.prepare_indicators(btc)
    
    close_prices = prepared_df["Close_clean"]
    
    # =========================
    # BUY & HOLD BENCHMARK
    # =========================
    first_price = close_prices.iloc[0]
    last_price = close_prices.iloc[-1]
    
    buy_hold_return = ((last_price - first_price) / first_price) * 100

    # =========================
    # STRATEGY VARIABLES
    # =========================
    position = None
    buy_price = 0
    buy_date = None
    
    trades = 0
    wins = 0
    losses = 0
    total_return = 0
    
    # Portfolio tracking
    cash = starting_capital
    units = 0
    trade_log = []
    equity_curve = []

    if verbose:
        print("=" * 50)
        print(f"TradeSense Backtest - Strategy: {strategy.name}")
        print("=" * 50)
        print()

    # Determine starting index based on first valid row of indicators
    # Drop indicator columns to see where we can start
    indicator_cols = [col for col in prepared_df.columns if col not in ["Close_clean", "Open", "High", "Low", "Volume", "Adj Close"]]
    non_nan_df = prepared_df.dropna(subset=indicator_cols)
    
    if len(non_nan_df) == 0:
        start_idx = 50 # Fallback
    else:
        # Get integer index of the first non-NaN row
        first_valid_date = non_nan_df.index[0]
        start_idx = prepared_df.index.get_loc(first_valid_date)

    # In legacy mode, we match the original loop range and off-by-one behavior
    if legacy_mode:
        # The original code runs: for i in range(50, len(close_prices))
        # and checks: current_price = historical_data.iloc[-1] (which is index i - 1)
        loop_range = range(50, len(close_prices))
    else:
        # In non-legacy mode, we run from start_idx to the end of the dataframe,
        # using the current index directly.
        loop_range = range(start_idx, len(close_prices))

    for i in loop_range:
        # In legacy mode, the current row traded is at index i - 1
        idx = (i - 1) if legacy_mode else i
        
        row = prepared_df.iloc[idx]
        current_price = row["Close_clean"]
        current_date = prepared_df.index[idx].date()
        
        # Get signal from pre-computed indicators at this index
        signal = strategy.generate_signal(prepared_df, idx)

        # Record portfolio value before action
        portfolio_value = cash + (units * current_price)
        equity_curve.append({
            "date": current_date,
            "portfolio_value": portfolio_value,
            "cash": cash,
            "units": units,
            "price": current_price
        })

        # =========================
        # ENTER TRADE
        # =========================
        if signal == "BUY" and position is None:
            position = "LONG"
            buy_price = current_price
            buy_date = current_date
            
            # Sizing: Buy 100% of cash
            units = cash / current_price
            cash = 0
            
            if verbose:
                print(f"{current_date} | BUY @ ${buy_price:.2f}")

        # =========================
        # EXIT TRADE
        # =========================
        elif signal == "SELL" and position == "LONG":
            sell_price = current_price
            profit_pct = ((sell_price - buy_price) / buy_price) * 100
            
            # Close position: sell all units
            cash = units * sell_price
            units = 0
            
            trades += 1
            total_return += profit_pct
            
            if profit_pct > 0:
                wins += 1
            else:
                losses += 1
                
            trade_log.append({
                "trade_num": trades,
                "entry_date": buy_date,
                "entry_price": buy_price,
                "exit_date": current_date,
                "exit_price": sell_price,
                "profit_pct": profit_pct,
                "portfolio_value": cash
            })

            if verbose:
                print(f"{current_date} | SELL @ ${sell_price:.2f}")
                print(f"Trade #{trades} Profit: {profit_pct:.2f}%")
                print()

            position = None

    # End of backtest: compute final portfolio value
    final_price = close_prices.iloc[-1]
    final_portfolio_value = cash + (units * final_price)
    portfolio_return = ((final_portfolio_value - starting_capital) / starting_capital) * 100

    if trades > 0:
        win_rate = (wins / trades) * 100
        average_trade = (total_return / trades)
    else:
        win_rate = 0
        average_trade = 0

    if verbose:
        print("=" * 50)
        print("Backtest Complete")
        print("=" * 50)
        print()
        print("Trades Closed:", trades)
        print()
        print("Wins:", wins)
        print("Losses:", losses)
        print()
        print("Win Rate:", round(win_rate, 2), "%")
        print("Total Return (Sum):", round(total_return, 2), "%")
        print("Average Trade:", round(average_trade, 2), "%")
        print()
        print("Portfolio Return (Compounded):", round(portfolio_return, 2), "%")
        print(f"Starting Capital: ${starting_capital:,.2f}")
        print(f"Final Capital: ${final_portfolio_value:,.2f}")
        print()
        print("=" * 50)
        print("BUY & HOLD COMPARISON")
        print("=" * 50)
        print()
        print("Buy & Hold Return:", round(buy_hold_return, 2), "%")
        print("TradeSense Return (Sum):", round(total_return, 2), "%")
        print("TradeSense Portfolio Return:", round(portfolio_return, 2), "%")
        print()

        if portfolio_return > buy_hold_return:
            print("✅ TradeSense beat Buy & Hold")
        elif portfolio_return < buy_hold_return:
            print("❌ TradeSense underperformed Buy & Hold")
        else:
            print("🤝 TradeSense matched Buy & Hold")

    return {
        "strategy_name": strategy.name,
        "trades_closed": trades,
        "wins": wins,
        "losses": losses,
        "win_rate": win_rate,
        "total_return_sum": total_return,
        "average_trade": average_trade,
        "portfolio_return": portfolio_return,
        "starting_capital": starting_capital,
        "final_capital": final_portfolio_value,
        "buy_hold_return": buy_hold_return,
        "trade_log": trade_log,
        "equity_curve": pd.DataFrame(equity_curve)
    }

if __name__ == "__main__":
    run_backtest()