import pandas as pd
from research.experiment import Experiment
from research.database import add_experiment
from backtesting.ranking import calculate_composite_score

def track_backtest_run(backtest_res: dict, robustness_score: float = 50.0, walk_forward_score: float = 0.0) -> Experiment:
    """
    Tracks a standard backtest run and logs it to the research database.
    """
    # Extract dates
    equity_curve = backtest_res["equity_curve"]
    if not equity_curve.empty:
        start_date = str(equity_curve.index[0])
        end_date = str(equity_curve.index[-1])
    else:
        start_date = ""
        end_date = ""

    # Calculate composite score if not already present
    composite_score = backtest_res.get("composite_score")
    if composite_score is None:
        composite_score = calculate_composite_score(
            portfolio_return=backtest_res["portfolio_return"],
            max_drawdown=backtest_res["max_drawdown"],
            sharpe=backtest_res["sharpe"],
            robustness=robustness_score
        )

    # Create Experiment
    exp = Experiment(
        strategy_name=backtest_res["strategy_name"],
        parameters=backtest_res.get("parameters", {}), # If strategy parameters are not directly returned, we can fall back to strategy params
        portfolio_return=backtest_res["portfolio_return"],
        sharpe=backtest_res["sharpe"],
        sortino=backtest_res["sortino"],
        max_drawdown=backtest_res["max_drawdown"],
        robustness=robustness_score,
        walk_forward_score=walk_forward_score,
        composite_score=composite_score,
        symbol="BTC-USD",
        start_date=start_date,
        end_date=end_date
    )
    
    # Save to DB
    add_experiment(exp)
    return exp

def track_optimization_run(strategy_name: str, best_params: dict, best_res_row: pd.Series, param_grid: dict, symbol: str = "BTC-USD", start_date: str = "", end_date: str = ""):
    """
    Tracks the best configuration from an optimization run.
    """
    # We estimate robustness using default/average of the runs or let it be populated.
    # We will compute the composite score
    score = calculate_composite_score(
        portfolio_return=best_res_row["portfolio_return_pct"],
        max_drawdown=best_res_row["max_drawdown"] if "max_drawdown" in best_res_row else 50.0, # fallback if missing
        sharpe=best_res_row["sharpe"] if "sharpe" in best_res_row else 0.5,
        robustness=50.0 # Default fallback
    )
    
    exp = Experiment(
        strategy_name=strategy_name,
        parameters=best_params,
        portfolio_return=best_res_row["portfolio_return_pct"],
        sharpe=best_res_row.get("sharpe", 0.0),
        sortino=best_res_row.get("sortino", 0.0),
        max_drawdown=best_res_row.get("max_drawdown", 0.0),
        robustness=50.0,
        composite_score=score,
        symbol=symbol,
        start_date=start_date,
        end_date=end_date
    )
    
    add_experiment(exp)
    return exp
