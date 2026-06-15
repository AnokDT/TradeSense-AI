import pandas as pd
from backtesting.backtest import run_backtest
from backtesting.robustness import analyze_robustness
from backtesting.ranking import calculate_composite_score

def compare_strategies(strategies, starting_capital: float = 10000.0, legacy_mode: bool = False):
    """
    Compares multiple strategies side-by-side on the same historical data,
    ranking them using a composite risk-adjusted score.
    """
    comparison_data = []
    
    print("=" * 80)
    print("TradeSense AI Strategy Comparison Report (Risk-Adjusted Composite Ranking)")
    print("=" * 80)
    print(f"Starting Capital: ${starting_capital:,.2f}")
    print(f"Strategies evaluated: {len(strategies)}")
    print()
    
    # Fetch historical data once
    from data.fetch_data import get_btc_data
    btc = get_btc_data()
    
    for strategy in strategies:
        # Run backtest silently
        res = run_backtest(
            strategy=strategy,
            starting_capital=starting_capital,
            legacy_mode=legacy_mode,
            verbose=False,
            export=False,
            data=btc
        )
        
        # Calculate robustness score via sensitivity analysis
        try:
            params = strategy.get_parameters()
            if "Price Crossover" in strategy.name:
                rob, _ = analyze_robustness(
                    type(strategy), params, "ema_period",
                    starting_capital=starting_capital, legacy_mode=legacy_mode, verbose=False, data=btc
                )
            elif "EMA Crossover" in strategy.name:
                rob, _ = analyze_robustness(
                    type(strategy), params, "fast_period",
                    starting_capital=starting_capital, legacy_mode=legacy_mode, verbose=False, data=btc
                )
            else:
                rob = 50.0
        except Exception:
            rob = 50.0
            
        # Compute composite score
        score = calculate_composite_score(
            portfolio_return=res["portfolio_return"],
            max_drawdown=res["max_drawdown"],
            sharpe=res["sharpe"],
            robustness=rob
        )
        
        win_rate = res["win_rate"]
        portfolio_return = res["portfolio_return"]
        buy_hold_return = res["buy_hold_return"]
        beat_bh = "Yes ✅" if portfolio_return > buy_hold_return else "No ❌"
        
        comparison_data.append({
            "Strategy Name": strategy.name,
            "Trades": res["trades_closed"],
            "Win Rate (%)": round(win_rate, 2),
            "Max DD (%)": round(res["max_drawdown"], 2),
            "Sharpe": round(res["sharpe"], 2),
            "Robustness": round(rob, 2),
            "Return (%)": round(portfolio_return, 2),
            "Composite Score": round(score, 2),
            "Beat B&H?": beat_bh
        })
        
    df_compare = pd.DataFrame(comparison_data)
    
    # Sort by Composite Score descending
    df_compare = df_compare.sort_values(by="Composite Score", ascending=False).reset_index(drop=True)
    
    # Print comparison table
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 1000)
    print(df_compare.to_string(index=True))
    print()
    print("=" * 80)
    
    # Identify the winner
    if len(df_compare) > 0:
        winner = df_compare.iloc[0]
        print(f"🏆 COMPOSITE WINNER: {winner['Strategy Name']}")
        print(f"   Composite Score:  {winner['Composite Score']:.2f} / 100.0")
        print(f"   Portfolio Return: {winner['Return (%)']:.2f}% (Max Drawdown: {winner['Max DD (%)']:.2f}%, Sharpe: {winner['Sharpe']:.2f})")
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
