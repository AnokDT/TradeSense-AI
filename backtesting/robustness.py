import numpy as np
import pandas as pd
from backtesting.backtest import run_backtest

def analyze_robustness(strategy_class, base_params: dict, param_name: str, step: int = 1, count: int = 5, starting_capital: float = 10000.0, legacy_mode: bool = False, verbose: bool = True, data: pd.DataFrame = None):
    """
    Analyzes parameter sensitivity and calculates a robustness score.
    Runs backtests for a range of parameter values around the base value.
    
    Parameters:
    - strategy_class: Strategy class to test
    - base_params: Dictionary of base parameters (e.g. {"ema_period": 50})
    - param_name: Name of the parameter to perturb (e.g. "ema_period")
    - step: Incremental step size for perturbation
    - count: Number of configurations to test (should be odd, e.g. 5)
    - data: Optional historical data DataFrame to prevent repeated downloads
    """
    if param_name not in base_params:
        raise ValueError(f"Parameter {param_name} not found in base_params")
        
    if data is None:
        from data.fetch_data import get_btc_data
        data = get_btc_data()
        
    base_val = base_params[param_name]
    half = count // 2
    
    # Generate neighbor values
    param_values = []
    for i in range(-half, half + 1):
        val = base_val + i * step
        if val > 0: # Ensure parameter is positive
            param_values.append(val)
            
    results = []
    
    if verbose:
        print("=" * 70)
        print(f"Robustness Analysis for {strategy_class.__name__}")
        print(f"Perturbing parameter: '{param_name}' around base value: {base_val}")
        print("=" * 70)
        print()

    for val in param_values:
        params = base_params.copy()
        params[param_name] = val
        
        # Instantiate strategy
        strategy = strategy_class(**params)
        
        # Run backtest silently
        res = run_backtest(
            strategy=strategy,
            starting_capital=starting_capital,
            legacy_mode=legacy_mode,
            verbose=False,
            export=False,
            data=data
        )
        
        results.append({
            "param_value": val,
            "trades": res["trades_closed"],
            "win_rate": res["win_rate"],
            "portfolio_return": res["portfolio_return"],
            "max_drawdown": res["max_drawdown"],
            "sharpe": res["sharpe"]
        })
        
    df_results = pd.DataFrame(results)
    
    # Calculate robustness score
    returns = df_results["portfolio_return"].values
    mean_ret = np.mean(returns)
    std_ret = np.std(returns)
    
    # 1. Profitable fraction (0.0 to 1.0)
    profitable_fraction = sum(1 for r in returns if r > 0) / len(returns)
    
    # 2. Stability coefficient
    if mean_ret > 0:
        cv = std_ret / mean_ret  # Coefficient of variation
        stability = 1.0 / (1.0 + cv)
    else:
        stability = 0.0
        
    robustness_score = 100.0 * profitable_fraction * stability
    
    if verbose:
        print(df_results.to_string(index=False))
        print("-" * 70)
        print(f"Mean Portfolio Return: {mean_ret:.2f}%")
        print(f"Std Dev of Returns:    {std_ret:.2f}%")
        print(f"Profitable Fraction:   {profitable_fraction * 100:.1f}%")
        print(f"Stability Factor:      {stability:.4f}")
        print(f"👉 Robustness Score:   {robustness_score:.2f} / 100.0")
        print("=" * 70)
        
    return robustness_score, df_results

if __name__ == "__main__":
    from strategy.ema_price_crossover import EMAPriceCrossoverStrategy
    analyze_robustness(
        EMAPriceCrossoverStrategy,
        {"ema_period": 50},
        "ema_period",
        step=1,
        count=5
    )
