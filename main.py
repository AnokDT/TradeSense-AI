# =========================
# TradeSense AI
# Main Program
# =========================

import sys
import pandas as pd

# ----- Imports -----
from data.fetch_data import get_btc_data
from indicators.ema import calculate_ema, get_trend
from indicators.rsi import calculate_rsi, get_rsi_signal
from indicators.volume import get_volume_signal
from strategy.reasons import get_reasons
from strategy.scoring import calculate_score

# Phase 2 & 3 Imports
from strategy.ema_price_crossover import EMAPriceCrossoverStrategy
from strategy.ema_crossover import EMACrossoverStrategy
from backtesting.backtest import run_backtest
from backtesting.optimizer import optimize_parameters
from backtesting.comparison import compare_strategies
from backtesting.robustness import analyze_robustness
from backtesting.walk_forward import run_walk_forward_validation

# Phase 4 Imports
from research.benchmark import run_benchmark_suite, export_research_report, export_multi_asset_report
from research.query import get_all_experiments, get_top_n_strategies, get_best_strategy_by_metric

def run_daily_analysis():
    print("\n" + "=" * 40)
    print("Running Daily Market Analysis...")
    print("=" * 40)
    
    # =========================
    # 1. FETCH MARKET DATA
    # =========================
    btc = get_btc_data()
    
    # Flatten MultiIndex columns if present to be clean
    if isinstance(btc.columns, pd.MultiIndex):
        btc.columns = [col[0] for col in btc.columns]
        
    close_prices = btc["Close"]
    volume_data = btc["Volume"]

    # =========================
    # 2. CALCULATE EMA
    # =========================
    ema50 = calculate_ema(close_prices, 50)
    ema200 = calculate_ema(close_prices, 200)

    latest_ema50 = ema50.iloc[-1]
    latest_ema200 = ema200.iloc[-1]

    trend = get_trend(
        latest_ema50,
        latest_ema200
    )

    # =========================
    # 3. CALCULATE RSI
    # =========================
    rsi = calculate_rsi(close_prices)
    latest_rsi = rsi.iloc[-1]
    rsi_signal = get_rsi_signal(latest_rsi)

    # =========================
    # 4. CALCULATE VOLUME
    # =========================
    volume_signal = get_volume_signal(volume_data)

    # =========================
    # 5. CALCULATE SCORES
    # =========================
    bull_score, bear_score = calculate_score(
        trend,
        rsi_signal,
        volume_signal
    )

    reasons = get_reasons(
        trend,
        rsi_signal,
        volume_signal
    )

    # =========================
    # 6. DETERMINE ACTION
    # =========================
    if bull_score > bear_score:
        action = "BUY"
    elif bear_score > bull_score:
        action = "SELL"
    else:
        action = "WAIT"

    # =========================
    # 7. CALCULATE CONFIDENCE
    # =========================
    total_score = bull_score + bear_score
    if total_score > 0:
        confidence = round(
            max(bull_score, bear_score) / total_score * 100,
            1
        )
    else:
        confidence = 50

    # =========================
    # 8. SIGNAL STRENGTH
    # =========================
    if confidence >= 85:
        strength = "VERY STRONG"
    elif confidence >= 70:
        strength = "STRONG"
    elif confidence >= 60:
        strength = "MODERATE"
    else:
        strength = "WEAK"

    # =========================
    # 9. DISPLAY RESULTS
    # =========================
    print()
    print("=" * 40)
    print("TradeSense AI Analysis Results")
    print("=" * 40)
    print()
    print("Current Price:", round(close_prices.iloc[-1], 2))
    print()
    print("EMA50:", round(latest_ema50, 2))
    print("EMA200:", round(latest_ema200, 2))
    print()
    print("Trend:", trend)
    print()
    print("Volume Signal:", volume_signal)
    print("RSI:", round(latest_rsi, 2))
    print("RSI Signal:", rsi_signal)
    print()
    print("Bull Score:", bull_score)
    print("Bear Score:", bear_score)
    print()
    print("Action:", action)
    print("Confidence:", confidence, "%")
    print("Signal Strength:", strength)
    print()
    print("Reasons:")
    for reason in reasons:
        print("-", reason)
    print()
    print("=" * 40)

def handle_backtest_menu():
    while True:
        print("\n" + "-" * 40)
        print("Backtesting Menu")
        print("-" * 40)
        print("1. Run EMA Price Crossover (EMA 50) - Legacy Mode")
        print("2. Run EMA Price Crossover (EMA 50) - Realistic Mode")
        print("3. Run EMA Crossover (EMA 50 vs EMA 200)")
        print("4. Back to Main Menu")
        print("-" * 40)
        
        choice = input("Select an option: ").strip()
        if choice == "1":
            strategy = EMAPriceCrossoverStrategy(50)
            run_backtest(strategy, legacy_mode=True)
            break
        elif choice == "2":
            strategy = EMAPriceCrossoverStrategy(50)
            run_backtest(strategy, legacy_mode=False)
            break
        elif choice == "3":
            strategy = EMACrossoverStrategy(50, 200)
            run_backtest(strategy, legacy_mode=False)
            break
        elif choice == "4":
            break
        else:
            print("Invalid selection. Please choose 1-4.")

def handle_optimization_menu():
    while True:
        print("\n" + "-" * 40)
        print("Parameter Optimization Menu")
        print("-" * 40)
        print("1. Optimize EMA Price Crossover Strategy")
        print("2. Optimize EMA Crossover Strategy")
        print("3. Back to Main Menu")
        print("-" * 40)
        
        choice = input("Select an option: ").strip()
        if choice == "1":
            grid = {"ema_period": [10, 20, 30, 50, 75, 100, 150, 200]}
            optimize_parameters(EMAPriceCrossoverStrategy, grid, legacy_mode=False)
            break
        elif choice == "2":
            grid = {
                "fast_period": [10, 20, 30, 50],
                "slow_period": [100, 150, 200]
            }
            optimize_parameters(EMACrossoverStrategy, grid, legacy_mode=False)
            break
        elif choice == "3":
            break
        else:
            print("Invalid selection. Please choose 1-3.")

def handle_comparison_menu():
    print("\nRunning multi-strategy comparison framework...")
    strategies = [
        EMAPriceCrossoverStrategy(50),
        EMAPriceCrossoverStrategy(100),
        EMACrossoverStrategy(50, 200),
        EMACrossoverStrategy(20, 100)
    ]
    compare_strategies(strategies, legacy_mode=False)

def handle_walk_forward_menu():
    while True:
        print("\n" + "-" * 40)
        print("Walk-Forward Validation Menu")
        print("-" * 40)
        print("1. Validate EMA Price Crossover Strategy")
        print("2. Validate EMA Crossover Strategy")
        print("3. Back to Main Menu")
        print("-" * 40)
        
        choice = input("Select an option [1-3]: ").strip()
        if choice == "1":
            grid = {"ema_period": [20, 50, 100, 150]}
            run_walk_forward_validation(EMAPriceCrossoverStrategy, grid, legacy_mode=False)
            break
        elif choice == "2":
            grid = {
                "fast_period": [10, 20, 30, 50],
                "slow_period": [100, 150, 200]
            }
            run_walk_forward_validation(EMACrossoverStrategy, grid, legacy_mode=False)
            break
        elif choice == "3":
            break
        else:
            print("Invalid selection. Please choose 1-3.")

def handle_robustness_menu():
    while True:
        print("\n" + "-" * 40)
        print("Parameter Robustness Menu")
        print("-" * 40)
        print("1. Analyze EMA Price Crossover (base: EMA 50)")
        print("2. Analyze EMA Price Crossover (base: EMA 100)")
        print("3. Analyze EMA Crossover (base: 50 vs 200)")
        print("4. Back to Main Menu")
        print("-" * 40)
        
        choice = input("Select an option [1-4]: ").strip()
        if choice == "1":
            analyze_robustness(EMAPriceCrossoverStrategy, {"ema_period": 50}, "ema_period", step=1, count=5, legacy_mode=False)
            break
def handle_view_database_summary():
    experiments = get_all_experiments()
    if not experiments:
        print("\nNo experiments found in database. Run option 8 first.")
        return
        
    print("\n" + "=" * 70)
    print("Research Database Summary")
    print("=" * 70)
    print(f"Total Saved Experiments: {len(experiments)}")
    print()
    
    for metric in ['return', 'sharpe', 'drawdown', 'robustness', 'composite_score']:
        try:
            best = get_best_strategy_by_metric(metric)
            if not best:
                continue
                
            label = {
                'return': "Best Return",
                'sharpe': "Best Sharpe",
                'drawdown': "Lowest Drawdown",
                'robustness': "Most Robust",
                'composite_score': "Best Composite"
            }[metric]
            
            val_suffix = "%" if metric in ['return', 'drawdown', 'robustness'] else ""
            val = best.get(metric, 0.0)
            if metric == 'drawdown':
                val = best.get("drawdown", 0.0)
                
            print(f"{label:<17}: {best.get('strategy_name')} | Params: {best.get('parameters')} | Value: {val:.2f}{val_suffix}")
        except Exception as e:
            print(f"Error loading metric {metric}: {e}")
    print("=" * 70)

def handle_show_top_strategies():
    n_str = input("\nEnter number of top strategies to show (default: 5): ").strip()
    n = int(n_str) if n_str.isdigit() else 5
    
    top = get_top_n_strategies(n)
    if not top:
        print("No strategies found in database. Run option 8 first.")
        return
        
    print("\n" + "=" * 110)
    print(f"Top {len(top)} Ranked Strategies (Sorted by Composite Score)")
    print("=" * 110)
    
    df = pd.DataFrame(top)
    display_cols = ["strategy_name", "parameters", "return", "drawdown", "sharpe", "robustness", "walk_forward_score", "composite_score"]
    df_print = df[[c for c in display_cols if c in df.columns]].copy()
    df_print.columns = ["Strategy", "Params", "Return (%)", "Max DD (%)", "Sharpe", "Robustness", "Walk-Forward", "Composite Score"]
    
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 1000)
    print(df_print.to_string(index=True))
    print("=" * 110)

def handle_reset_database():
    confirm = input("\nAre you sure you want to reset the research database? [y/N]: ").strip().lower()
    if confirm == 'y':
        from research.database import save_database
        save_database([])
        print("Research database cleared successfully.")

def main_menu():
    while True:
        print("\n" + "=" * 55)
        print("TradeSense AI - Professional Quantitative Research")
        print("=" * 55)
        print("1. Run Daily Market Analysis")
        print("2. Run Strategy Backtests (Risk & Perf Report)")
        print("3. Optimize Strategy Parameters")
        print("4. Compare Strategies (Composite Score)")
        print("5. Run Walk-Forward Validation")
        print("6. Run Parameter Robustness Analysis")
        print("7. Reset Research Database")
        print("8. Run Full Strategy Benchmark Suite")
        print("9. View Research Database Summary")
        print("10. Show Top Ranked Strategies")
        print("11. Export Research Report")
        print("12. Exit")
        print("=" * 55)
        
        choice = input("Select an option [1-12]: ").strip()
        if choice == "1":
            run_daily_analysis()
        elif choice == "2":
            handle_backtest_menu()
        elif choice == "3":
            handle_optimization_menu()
        elif choice == "4":
            handle_comparison_menu()
        elif choice == "5":
            handle_walk_forward_menu()
        elif choice == "6":
            handle_robustness_menu()
        elif choice == "7":
            handle_reset_database()
        elif choice == "8":
            run_benchmark_suite(legacy_mode=False)
        elif choice == "9":
            handle_view_database_summary()
        elif choice == "10":
            handle_show_top_strategies()
        elif choice == "11":
            export_research_report()
        elif choice == "12":
            print("\nThank you for using TradeSense AI. Goodbye!\n")
            sys.exit(0)
        else:
            print("Invalid selection. Please choose 1-12.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg == "analysis":
            run_daily_analysis()
        elif arg == "backtest":
            run_backtest(EMAPriceCrossoverStrategy(50), legacy_mode=True)
        elif arg == "compare":
            handle_comparison_menu()
        elif arg == "walkforward":
            grid = {"ema_period": [20, 50, 100]}
            run_walk_forward_validation(EMAPriceCrossoverStrategy, grid, legacy_mode=False)
        elif arg == "robustness":
            analyze_robustness(EMAPriceCrossoverStrategy, {"ema_period": 50}, "ema_period", step=1, count=5, legacy_mode=False)
        elif arg == "benchmark":
            run_benchmark_suite(legacy_mode=False)
        elif arg == "benchmark_multi":
            run_benchmark_suite(symbols=["BTC-USD", "ETH-USD", "SOL-USD", "BNB-USD"], legacy_mode=False)
            export_multi_asset_report(symbols=["BTC-USD", "ETH-USD", "SOL-USD", "BNB-USD"])
        else:
            print(f"Unknown argument: {arg}")
    else:
        main_menu()

