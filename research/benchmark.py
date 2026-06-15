import os
import json
import pandas as pd
from data.fetch_data import get_btc_data
from backtesting.backtest import run_backtest
from backtesting.robustness import analyze_robustness
from backtesting.walk_forward import run_walk_forward_validation
from research.experiment_tracker import track_backtest_run
from research.query import get_all_experiments, get_best_strategy_by_metric

# Import Strategy Classes
from strategy.ema_price_crossover import EMAPriceCrossoverStrategy
from strategy.ema_crossover import EMACrossoverStrategy
from strategy.sma_crossover import SMACrossoverStrategy
from strategy.macd_strategy import MACDStrategy
from strategy.supertrend_strategy import SupertrendStrategy
from strategy.donchian_breakout import DonchianBreakoutStrategy
from strategy.rsi_strategy import RSIStrategy
from strategy.bollinger_strategy import BollingerBandsStrategy
from strategy.atr_breakout import ATRBreakoutStrategy

BENCHMARK_CONFIGS = {
    "ema_price": {
        "class": EMAPriceCrossoverStrategy,
        "base_params": {"ema_period": 50},
        "param_name": "ema_period",
        "grid": {"ema_period": [20, 50, 100]}
    },
    "ema_cross": {
        "class": EMACrossoverStrategy,
        "base_params": {"fast_period": 50, "slow_period": 200},
        "param_name": "fast_period",
        "grid": {"fast_period": [20, 50], "slow_period": [100, 200]}
    },
    "sma_cross": {
        "class": SMACrossoverStrategy,
        "base_params": {"fast_period": 20, "slow_period": 50},
        "param_name": "fast_period",
        "grid": {"fast_period": [10, 20], "slow_period": [50, 100]}
    },
    "macd": {
        "class": MACDStrategy,
        "base_params": {"fast_period": 12, "slow_period": 26, "signal_period": 9},
        "param_name": "fast_period",
        "grid": {"fast_period": [12, 24], "slow_period": [26, 50], "signal_period": [9]}
    },
    "supertrend": {
        "class": SupertrendStrategy,
        "base_params": {"atr_period": 10, "multiplier": 3.0},
        "param_name": "atr_period",
        "grid": {"atr_period": [10, 14], "multiplier": [2.5, 3.0]}
    },
    "donchian": {
        "class": DonchianBreakoutStrategy,
        "base_params": {"lookback_period": 20},
        "param_name": "lookback_period",
        "grid": {"lookback_period": [10, 20, 30]}
    },
    "rsi": {
        "class": RSIStrategy,
        "base_params": {"rsi_period": 14, "oversold": 30, "overbought": 70},
        "param_name": "rsi_period",
        "grid": {"rsi_period": [10, 14], "oversold": [30], "overbought": [70]}
    },
    "bollinger": {
        "class": BollingerBandsStrategy,
        "base_params": {"period": 20, "std_dev": 2.0},
        "param_name": "period",
        "grid": {"period": [10, 20], "std_dev": [2.0]}
    },
    "atr_breakout": {
        "class": ATRBreakoutStrategy,
        "base_params": {"atr_period": 14, "multiplier": 1.5},
        "param_name": "atr_period",
        "grid": {"atr_period": [10, 14], "multiplier": [1.5, 2.0]}
    }
}

def run_benchmark_suite(starting_capital: float = 10000.0, legacy_mode: bool = False):
    """
    Evaluates all registered strategy families and logs them to the research database.
    """
    btc = get_btc_data()
    
    if isinstance(btc.columns, pd.MultiIndex):
        btc.columns = [col[0] for col in btc.columns]

    print("=" * 80)
    print("TradeSense AI - Strategy Benchmark Suite")
    print("=" * 80)
    print(f"Starting capital: ${starting_capital:,.2f}")
    print(f"Total strategy families: {len(BENCHMARK_CONFIGS)}")
    print()

    for key, config in BENCHMARK_CONFIGS.items():
        print(f"Evaluating Strategy: {config['class'].__name__} ...")
        
        # 1. Backtest
        strategy = config["class"](**config["base_params"])
        res = run_backtest(
            strategy=strategy,
            starting_capital=starting_capital,
            legacy_mode=legacy_mode,
            verbose=False,
            export=False,
            data=btc
        )
        
        # 2. Robustness Check
        try:
            rob, _ = analyze_robustness(
                config["class"], config["base_params"], config["param_name"],
                starting_capital=starting_capital, legacy_mode=legacy_mode, verbose=False, data=btc
            )
        except Exception:
            rob = 50.0
            
        # 3. Walk-Forward
        try:
            wf_res = run_walk_forward_validation(
                config["class"], config["grid"],
                starting_capital=starting_capital, legacy_mode=legacy_mode, verbose=False, data=btc
            )
            wf_score = wf_res["robustness_score"]
        except Exception:
            wf_score = 0.0

        # Track and log to DB
        track_backtest_run(res, robustness_score=rob, walk_forward_score=wf_score)
        print(f"   Return: {res['portfolio_return']:.2f}% | Sharpe: {res['sharpe']:.2f} | MDD: {res['max_drawdown']:.2f}% | Rob: {rob:.1f} | WF: {wf_score:.1f}%")
        print()

    print("=" * 80)
    print("Benchmark Suite Completed Successfully.")
    print("=" * 80)

def export_research_report():
    """
    Generates and saves research summary files under results/.
    """
    experiments = get_all_experiments()
    if not experiments:
        print("No experiments found in database. Run benchmark suite first.")
        return
        
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    results_dir = os.path.join(project_root, "results")
    os.makedirs(results_dir, exist_ok=True)
    
    # 1. Save top strategies sorted by composite score
    df_exp = pd.DataFrame(experiments)
    df_sorted = df_exp.sort_values(by="composite_score", ascending=False).reset_index(drop=True)
    df_sorted.to_csv(os.path.join(results_dir, "top_strategies.csv"), index=False)
    
    # 2. Extract best by key metrics
    best_return = get_best_strategy_by_metric("return")
    best_sharpe = get_best_strategy_by_metric("sharpe")
    lowest_dd = get_best_strategy_by_metric("drawdown")
    most_robust = get_best_strategy_by_metric("robustness")
    best_composite = get_best_strategy_by_metric("composite_score")
    
    summary = {
        "total_experiments": len(experiments),
        "best_return": {
            "strategy": best_return.get("strategy_name"),
            "parameters": best_return.get("parameters"),
            "value": best_return.get("return")
        },
        "best_sharpe": {
            "strategy": best_sharpe.get("strategy_name"),
            "parameters": best_sharpe.get("parameters"),
            "value": best_sharpe.get("sharpe")
        },
        "lowest_drawdown": {
            "strategy": lowest_dd.get("strategy_name"),
            "parameters": lowest_dd.get("parameters"),
            "value": lowest_dd.get("drawdown")
        },
        "most_robust": {
            "strategy": most_robust.get("strategy_name"),
            "parameters": most_robust.get("parameters"),
            "value": most_robust.get("robustness")
        },
        "best_composite": {
            "strategy": best_composite.get("strategy_name"),
            "parameters": best_composite.get("parameters"),
            "value": best_composite.get("composite_score")
        }
    }
    
    # Save research summary JSON
    with open(os.path.join(results_dir, "research_summary.json"), "w") as f:
        json.dump(summary, f, indent=2)
        
    print()
    print("=" * 80)
    print("Research Report Exported:")
    print(f"- Data:    {os.path.join(results_dir, 'top_strategies.csv')}")
    print(f"- Summary: {os.path.join(results_dir, 'research_summary.json')}")
    print("=" * 80)
