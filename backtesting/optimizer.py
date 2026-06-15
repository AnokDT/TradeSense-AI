import itertools
import pandas as pd
from backtesting.backtest import run_backtest

def optimize_parameters(strategy_class, param_grid, starting_capital: float = 10000.0, legacy_mode: bool = False):
    """
    Performs a grid search parameter optimization for a given strategy class.
    
    Parameters:
    - strategy_class: The strategy class to optimize (e.g. EMACrossoverStrategy).
    - param_grid: A dictionary mapping parameter names to lists/ranges of values to test.
    - starting_capital: Initial capital for the simulation (default: 10000.0).
    - legacy_mode: Whether to run backtests in legacy mode.
    """
    keys = list(param_grid.keys())
    values_list = [param_grid[key] for key in keys]
    combinations = list(itertools.product(*values_list))
    
    results = []
    
    print("=" * 70)
    print(f"Optimizing parameters for strategy: {strategy_class.__name__}")
    print("=" * 70)
    print(f"Total combinations to test: {len(combinations)}")
    print()
    
    for idx, comb in enumerate(combinations):
        params = dict(zip(keys, comb))
        
        # Instantiate strategy with parameters
        # Support passing parameters either by kwargs
        strategy = strategy_class(**params)
        
        # Run backtest silently
        res = run_backtest(
            strategy=strategy,
            starting_capital=starting_capital,
            legacy_mode=legacy_mode,
            verbose=False
        )
        
        results.append({
            **params,
            "trades": res["trades_closed"],
            "win_rate_pct": round(res["win_rate"], 2),
            "sum_return_pct": round(res["total_return_sum"], 2),
            "portfolio_return_pct": round(res["portfolio_return"], 2),
            "final_capital": round(res["final_capital"], 2)
        })
        
    # Convert to DataFrame
    df_results = pd.DataFrame(results)
    
    # Sort by portfolio_return_pct descending
    if "portfolio_return_pct" in df_results.columns:
        df_results = df_results.sort_values(by="portfolio_return_pct", ascending=False).reset_index(drop=True)
    
    # Format display columns
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 1000)
    
    print("Top 10 Configurations:")
    print("-" * 70)
    print(df_results.head(10).to_string(index=True))
    print("-" * 70)
    
    if len(df_results) > 0:
        best_row = df_results.iloc[0]
        best_params = {k: best_row[k] for k in keys}
        # Cast parameter types back to original type (int or float) from float64 if needed
        for k in best_params:
            if isinstance(param_grid[k][0], int):
                best_params[k] = int(best_params[k])
                
        print()
        print("=" * 70)
        print(f"Best Parameters: {best_params}")
        print(f"Best Portfolio Return: {best_row['portfolio_return_pct']:.2f}% (Final Capital: ${best_row['final_capital']:,.2f})")
        print("=" * 70)
        return best_params, df_results
    else:
        print("No results generated.")
        return {}, pd.DataFrame()

if __name__ == "__main__":
    # Test optimizer with EMAPriceCrossoverStrategy
    from strategy.ema_price_crossover import EMAPriceCrossoverStrategy
    grid = {
        "ema_period": [10, 20, 30, 50, 75, 100, 150, 200]
    }
    optimize_parameters(EMAPriceCrossoverStrategy, grid)
