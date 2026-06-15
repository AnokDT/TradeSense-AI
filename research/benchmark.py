import os
import json
import pandas as pd
from data.fetch_data import get_crypto_data
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

def run_benchmark_suite(symbols: list = None, starting_capital: float = 10000.0, legacy_mode: bool = False):
    """
    Evaluates all registered strategy families and logs them to the research database.
    """
    if symbols is None:
        symbols = ["BTC-USD"]

    for symbol in symbols:
        print("=" * 80)
        print(f"TradeSense AI - Strategy Benchmark Suite for {symbol}")
        print("=" * 80)
        print(f"Starting capital: ${starting_capital:,.2f}")
        print(f"Total strategy families: {len(BENCHMARK_CONFIGS)}")
        print()

        try:
            data = get_crypto_data(symbol)
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")
            continue
            
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = [col[0] for col in data.columns]

        for key, config in BENCHMARK_CONFIGS.items():
            print(f"Evaluating Strategy: {config['class'].__name__} on {symbol} ...")
            
            # 1. Backtest
            strategy = config["class"](**config["base_params"])
            res = run_backtest(
                strategy=strategy,
                starting_capital=starting_capital,
                legacy_mode=legacy_mode,
                verbose=False,
                export=False,
                data=data
            )
            
            # 2. Robustness Check
            try:
                rob, _ = analyze_robustness(
                    config["class"], config["base_params"], config["param_name"],
                    starting_capital=starting_capital, legacy_mode=legacy_mode, verbose=False, data=data
                )
            except Exception:
                rob = 50.0
                
            # 3. Walk-Forward
            try:
                wf_res = run_walk_forward_validation(
                    config["class"], config["grid"],
                    starting_capital=starting_capital, legacy_mode=legacy_mode, verbose=False, data=data
                )
                wf_score = wf_res["robustness_score"]
            except Exception:
                wf_score = 0.0

            # Track and log to DB
            track_backtest_run(res, robustness_score=rob, walk_forward_score=wf_score, symbol=symbol)
            print(f"   Return: {res['portfolio_return']:.2f}% | Sharpe: {res['sharpe']:.2f} | MDD: {res['max_drawdown']:.2f}% | Rob: {rob:.1f} | WF: {wf_score:.1f}%")
            print()

        print("=" * 80)
        print(f"Benchmark Suite for {symbol} Completed Successfully.")
        print("=" * 80)
        print()


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

def export_multi_asset_report(symbols: list = None):
    """
    Generates and saves multi-asset comparative research reports under results/.
    """
    if symbols is None:
        symbols = ["BTC-USD", "ETH-USD", "SOL-USD", "BNB-USD"]
        
    experiments = get_all_experiments()
    if not experiments:
        print("No experiments found in database.")
        return
        
    # Filter by requested symbols
    data_list = []
    for exp in experiments:
        if exp.get("symbol") in symbols:
            data_list.append(exp)

            
    if not data_list:
        print(f"No experiments found in database for symbols: {symbols}")
        return
        
    df = pd.DataFrame(data_list)
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    results_dir = os.path.join(project_root, "results")
    
    # Clean strategy names so we group by the base family rather than parameter details
    def get_strategy_family(name):
        if "(" in name:
            return name.split("(")[0].strip()
        return name
        
    df["strategy_family"] = df["strategy_name"].apply(get_strategy_family)
    
    # Save a raw symbol-by-strategy details CSV
    df.to_csv(os.path.join(results_dir, "multi_asset_raw_results.csv"), index=False)
    
    # Calculate average metrics for each strategy across ALL symbols
    df_grouped = df.groupby("strategy_family").agg({
        "return": "mean",
        "drawdown": "mean",
        "sharpe": "mean",
        "robustness": "mean",
        "walk_forward_score": "mean",
        "composite_score": "mean"
    }).reset_index()
    
    df_ranked = df_grouped.sort_values(by="composite_score", ascending=False).reset_index(drop=True)
    df_ranked.to_csv(os.path.join(results_dir, "multi_asset_rankings.csv"), index=False)
    
    # Identify specific categories
    # - Most robust: highest average robustness score
    most_robust_row = df_ranked.loc[df_ranked["robustness"].idxmax()]
    most_robust = most_robust_row["strategy_family"]
    most_robust_val = most_robust_row["robustness"]
    
    # - Highest return: highest average return
    highest_return_row = df_ranked.loc[df_ranked["return"].idxmax()]
    highest_return = highest_return_row["strategy_family"]
    highest_return_val = highest_return_row["return"]
    
    # - Lowest drawdown: lowest average max drawdown
    lowest_dd_row = df_ranked.loc[df_ranked["drawdown"].idxmin()]
    lowest_dd = lowest_dd_row["strategy_family"]
    lowest_dd_val = lowest_dd_row["drawdown"]
    
    # - Best risk-adjusted: highest average Sharpe
    best_risk_adj_row = df_ranked.loc[df_ranked["sharpe"].idxmax()]
    best_risk_adj = best_risk_adj_row["strategy_family"]
    best_risk_adj_val = best_risk_adj_row["sharpe"]

    
    # Consistent performers and overfitted strategies
    consistent_performers = []
    overfitted_strategies = []
    
    for family in df["strategy_family"].unique():
        family_df = df[df["strategy_family"] == family]
        if len(family_df) >= len(symbols):
            scores = family_df["composite_score"].values
            mean_score = scores.mean()
            std_score = scores.std()
            if mean_score > 50.0 and std_score < 18.0:
                consistent_performers.append(family)
                
            avg_rob = family_df["robustness"].mean()
            avg_wf = family_df["walk_forward_score"].mean()
            avg_ret = family_df["return"].mean()
            # If standard return is relatively high but robustness or walk forward is very low
            if avg_ret > 40.0 and (avg_rob < 60.0 or avg_wf < 50.0):
                overfitted_strategies.append(family)

    summary = {
        "total_assets_tested": len(symbols),
        "assets": symbols,
        "most_robust_strategy": {
            "strategy": most_robust,
            "value_pct": float(most_robust_val)
        },
        "highest_return_strategy": {
            "strategy": highest_return,
            "value_pct": float(highest_return_val)
        },
        "lowest_drawdown_strategy": {
            "strategy": lowest_dd,
            "value_pct": float(lowest_dd_val)
        },
        "best_risk_adjusted_strategy": {
            "strategy": best_risk_adj,
            "value": float(best_risk_adj_val)
        },
        "consistently_performing_strategies": sorted(consistent_performers),
        "overfitted_strategies_identified": sorted(overfitted_strategies),
        "rankings": df_ranked.to_dict(orient="records")
    }
    
    with open(os.path.join(results_dir, "multi_asset_summary.json"), "w") as f:
        json.dump(summary, f, indent=2)
        
    print()
    print("=" * 80)
    print("Multi-Asset Research Report Exported:")
    print(f"- Raw Data: {os.path.join(results_dir, 'multi_asset_raw_results.csv')}")
    print(f"- Rankings: {os.path.join(results_dir, 'multi_asset_rankings.csv')}")
    print(f"- Summary:  {os.path.join(results_dir, 'multi_asset_summary.json')}")
    print("=" * 80)
    print()

