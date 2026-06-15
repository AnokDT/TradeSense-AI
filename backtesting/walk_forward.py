import os
import pandas as pd
import numpy as np
from data.fetch_data import get_btc_data
from backtesting.backtest import run_backtest
from backtesting.optimizer import optimize_parameters

def run_walk_forward_validation(strategy_class, param_grid, train_span_years: int = 2, test_span_years: int = 1, starting_capital: float = 10000.0, legacy_mode: bool = False, verbose: bool = True):
    """
    Performs Walk-Forward Validation to evaluate a strategy and prevent overfitting.
    
    Process:
    1. Splits data into rolling windows of Training and Testing.
    2. Optimizes parameters on the training window.
    3. Runs backtest with optimized parameters on the out-of-sample testing window.
    4. Computes out-of-sample metrics.
    """
    btc = get_btc_data()
    
    if isinstance(btc.columns, pd.MultiIndex):
        btc.columns = [col[0] for col in btc.columns]
        
    start_date = btc.index[0]
    end_date = btc.index[-1]
    
    # Generate rolling yearly windows
    windows = []
    i = 0
    while True:
        train_start = start_date + pd.Timedelta(days=i * 365)
        train_end = train_start + pd.Timedelta(days=train_span_years * 365)
        test_start = train_end + pd.Timedelta(days=1)
        test_end = test_start + pd.Timedelta(days=test_span_years * 365)
        
        if test_end > end_date:
            break
            
        windows.append((train_start, train_end, test_start, test_end))
        i += 1
        
    if not windows:
        # Fallback to a single split if data is too short
        train_end = start_date + pd.Timedelta(days=int(total_days * 0.7))
        test_start = train_end + pd.Timedelta(days=1)
        windows.append((start_date, train_end, test_start, end_date))
        
    results = []
    
    if verbose:
        print("=" * 80)
        print(f"Walk-Forward Validation for {strategy_class.__name__}")
        print(f"Total rolling windows generated: {len(windows)}")
        print("=" * 80)
        print()

    for idx, (train_s, train_e, test_s, test_e) in enumerate(windows):
        if verbose:
            print(f"--- Window #{idx+1} ---")
            print(f"Training Period:   {train_s.date()} to {train_e.date()}")
            print(f"Testing Period:    {test_s.date()} to {test_e.date()} (OUT-OF-SAMPLE)")
            
        # 1. Optimize on training data
        df_train = btc.loc[train_s:train_e]
        best_params, opt_df = optimize_parameters(
            strategy_class=strategy_class,
            param_grid=param_grid,
            starting_capital=starting_capital,
            legacy_mode=legacy_mode,
            verbose=False,
            data=df_train
        )
        
        # 2. Run backtest on combined training + testing data, but only execute trades
        # during the testing window to keep indicator history intact
        df_combined = btc.loc[train_s:test_e]
        
        # Instantiate strategy with optimized params
        strategy = strategy_class(**best_params)
        
        res = run_backtest(
            strategy=strategy,
            starting_capital=starting_capital,
            legacy_mode=legacy_mode,
            verbose=False,
            export=False,
            data=df_combined,
            trade_start_date=test_s.date(),
            trade_end_date=test_e.date()
        )
        
        results.append({
            "window": idx + 1,
            "train_start": train_s.date(),
            "train_end": train_e.date(),
            "test_start": test_s.date(),
            "test_end": test_e.date(),
            "best_params": str(best_params),
            "oos_trades": res["trades_closed"],
            "oos_win_rate_pct": round(res["win_rate"], 2),
            "oos_return_pct": round(res["portfolio_return"], 2),
            "oos_drawdown_pct": round(res["max_drawdown"], 2),
            "oos_sharpe": round(res["sharpe"], 2),
            "oos_buy_hold_pct": round(res["buy_hold_return"], 2)
        })
        
        if verbose:
            print(f"Best Parameters Found:  {best_params}")
            print(f"OOS Trades Closed:      {res['trades_closed']}")
            print(f"OOS Return:             {res['portfolio_return']:.2f}% (B&H: {res['buy_hold_return']:.2f}%)")
            print(f"OOS Max Drawdown:       {res['max_drawdown']:.2f}%")
            print(f"OOS Sharpe Ratio:       {res['sharpe']:.2f}")
            print()

    df_results = pd.DataFrame(results)
    
    # Export results to results/validation.csv
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    results_dir = os.path.join(project_root, "results")
    os.makedirs(results_dir, exist_ok=True)
    df_results.to_csv(os.path.join(results_dir, "validation.csv"), index=False)
    
    # Calculate aggregate out-of-sample metrics
    avg_oos_return = df_results["oos_return_pct"].mean()
    avg_oos_drawdown = df_results["oos_drawdown_pct"].mean()
    
    # Robustness Score: fraction of out-of-sample windows that are profitable (0-100)
    profitable_windows = sum(1 for r in df_results["oos_return_pct"] if r > 0)
    robustness_score = (profitable_windows / len(df_results)) * 100.0
    
    if verbose:
        print("=" * 80)
        print("Walk-Forward Validation Summary")
        print("=" * 80)
        print(df_results[["window", "test_start", "test_end", "best_params", "oos_return_pct", "oos_drawdown_pct", "oos_buy_hold_pct"]].to_string(index=False))
        print("-" * 80)
        print(f"Average Out-of-Sample Return:   {avg_oos_return:.2f}%")
        print(f"Average Out-of-Sample Drawdown: {avg_oos_drawdown:.2f}%")
        print(f"Profitable Windows:             {profitable_windows} / {len(df_results)}")
        print(f"👉 Out-of-Sample Robustness Score: {robustness_score:.2f} / 100.0")
        print("=" * 80)
        
    return {
        "avg_oos_return": avg_oos_return,
        "avg_oos_drawdown": avg_oos_drawdown,
        "robustness_score": robustness_score,
        "window_results": df_results
    }

if __name__ == "__main__":
    from strategy.ema_price_crossover import EMAPriceCrossoverStrategy
    grid = {"ema_period": [20, 50, 100]}
    run_walk_forward_validation(EMAPriceCrossoverStrategy, grid)
