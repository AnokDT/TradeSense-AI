import pandas as pd
from backtesting.backtest import run_backtest

def compare_strategies(strategies, starting_capital: float = 10000.0, legacy_mode: bool = False):
    """
    Compares multiple strategies side-by-side on the same historical data.
    
    Parameters:
    - strategies: A list of strategy instances (e.g., [EMAPriceCrossoverStrategy(50), EMACrossoverStrategy(50, 200)])
    - starting_capital: Initial capital for backtesting (default: 10000.0)
    - legacy_mode: Whether to run backtests in legacy mode.
    """
    comparison_data = []
    
    print("=" * 80)
    print("TradeSense AI Strategy Comparison Report")
    print("=" * 80)
    print(f"Starting Capital: ${starting_capital:,.2f}")
    print(f"Strategies evaluated: {len(strategies)}")
    print()
    
    for strategy in strategies:
        # Run backtest silently
        res = run_backtest(
            strategy=strategy,
            starting_capital=starting_capital,
            legacy_mode=legacy_mode,
            verbose=False
        )
        
        # Calculate comparison metrics
        win_rate = res["win_rate"]
        portfolio_return = res["portfolio_return"]
        buy_hold_return = res["buy_hold_return"]
        beat_bh = "Yes ✅" if portfolio_return > buy_hold_return else "No ❌"
        
        comparison_data.append({
            "Strategy Name": strategy.name,
            "Trades Closed": res["trades_closed"],
            "Wins": res["wins"],
            "Losses": res["losses"],
            "Win Rate (%)": round(win_rate, 2),
            "Sum Return (%)": round(res["total_return_sum"], 2),
            "Portfolio Return (%)": round(portfolio_return, 2),
            "Final Capital ($)": round(res["final_capital"], 2),
            "B&H Return (%)": round(buy_hold_return, 2),
            "Beat B&H?": beat_bh
        })
        
    df_compare = pd.DataFrame(comparison_data)
    
    # Sort by Portfolio Return (%) descending
    df_compare = df_compare.sort_values(by="Portfolio Return (%)", ascending=False).reset_index(drop=True)
    
    # Print comparison table
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 1000)
    print(df_compare.to_string(index=True))
    print()
    print("=" * 80)
    
    # Identify the winner
    if len(df_compare) > 0:
        winner = df_compare.iloc[0]
        print(f"🏆 WINNER: {winner['Strategy Name']}")
        print(f"   Portfolio Return: {winner['Portfolio Return (%)']:.2f}% (Final Capital: ${winner['Final Capital ($)']:,.2f})")
        print("=" * 80)
        
    return df_compare

if __name__ == "__main__":
    from strategy.ema_price_crossover import EMAPriceCrossoverStrategy
    from strategy.ema_crossover import EMACrossoverStrategy
    
    # Compare original strategy vs EMA50/200 crossover vs Buy & Hold
    strategies = [
        EMAPriceCrossoverStrategy(50),
        EMAPriceCrossoverStrategy(100),
        EMACrossoverStrategy(50, 200),
        EMACrossoverStrategy(20, 100)
    ]
    compare_strategies(strategies)
