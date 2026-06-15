import os
import pandas as pd
from data.fetch_data import get_btc_data
from strategy.base import BaseStrategy
from strategy.ema_price_crossover import EMAPriceCrossoverStrategy
from backtesting.risk import (
    calculate_max_drawdown,
    calculate_volatility,
    calculate_sharpe_ratio,
    calculate_sortino_ratio,
    calculate_calmar_ratio
)
from reporting.charts import plot_equity_curve, plot_drawdown_curve

def run_backtest(strategy: BaseStrategy = None, starting_capital: float = 10000.0, legacy_mode: bool = True, verbose: bool = True, export: bool = True, data: pd.DataFrame = None, trade_start_date = None, trade_end_date = None):
    """
    Runs a historical backtest of the specified strategy.
    
    Parameters:
    - strategy: An instance of BaseStrategy (defaults to EMAPriceCrossoverStrategy(50))
    - starting_capital: The starting capital for the portfolio (default: 10000.0)
    - legacy_mode: If True, matches the off-by-one indexing of the original version for exact comparison.
    - verbose: If True, prints detailed log of trades and summary stats.
    - export: If True, exports trade logs and equity curve to results/ folder.
    - data: Optional DataFrame of historical data to use instead of downloading.
    - trade_start_date: Optional date to start trading from (inclusive).
    - trade_end_date: Optional date to end trading at (inclusive).
    """
    if strategy is None:
        strategy = EMAPriceCrossoverStrategy(50)

    # Fetch BTC data
    if data is None:
        btc = get_btc_data()
    else:
        btc = data.copy()
    
    # Prepare indicators using the strategy
    prepared_df = strategy.prepare_indicators(btc)
    
    close_prices = prepared_df["Close_clean"]
    
    # Determine starting index based on first valid row of indicators
    indicator_cols = [col for col in prepared_df.columns if col not in ["Close_clean", "Open", "High", "Low", "Volume", "Adj Close"]]
    non_nan_df = prepared_df.dropna(subset=indicator_cols)
    
    if len(non_nan_df) == 0:
        start_idx = 50 # Fallback
    else:
        first_valid_date = non_nan_df.index[0]
        start_idx = prepared_df.index.get_loc(first_valid_date)

    if legacy_mode:
        loop_range = range(50, len(close_prices))
    else:
        loop_range = range(start_idx, len(close_prices))

    # Bounded trading dates restriction
    if trade_start_date is not None:
        from datetime import date, datetime
        if isinstance(trade_start_date, str):
            ts_date = datetime.strptime(trade_start_date, "%Y-%m-%d").date()
        else:
            ts_date = trade_start_date
            
        dates = prepared_df.index
        start_idx_restricted = next((idx for idx, d in enumerate(dates) if d.date() >= ts_date), start_idx)
        loop_range = range(max(start_idx, start_idx_restricted), loop_range.stop)
        
    if trade_end_date is not None:
        from datetime import date, datetime
        if isinstance(trade_end_date, str):
            te_date = datetime.strptime(trade_end_date, "%Y-%m-%d").date()
        else:
            te_date = trade_end_date
            
        dates = prepared_df.index
        end_idx_restricted = next((idx for idx, d in enumerate(dates) if d.date() > te_date), len(close_prices))
        loop_range = range(loop_range.start, min(len(close_prices), end_idx_restricted))

    # =========================
    # BUY & HOLD BENCHMARK
    # =========================
    if len(loop_range) > 0:
        first_price = close_prices.iloc[loop_range[0]]
        last_price = close_prices.iloc[loop_range[-1]]
    else:
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
        print("=" * 60)
        print(f"TradeSense Backtest - Strategy: {strategy.name}")
        print("=" * 60)
        print()

    for i in loop_range:
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

    # Ensure we convert equity curve list to DataFrame
    df_equity = pd.DataFrame(equity_curve)
    
    # Calculate daily returns and running drawdowns
    if not df_equity.empty:
        # Set date as index
        df_equity.set_index("date", inplace=True)
        # Compute daily returns
        df_equity["daily_return"] = df_equity["portfolio_value"].pct_change().fillna(0.0)
        # Compute peaks and running drawdown series
        peaks = df_equity["portfolio_value"].cummax()
        df_equity["drawdown"] = (df_equity["portfolio_value"] - peaks) / peaks
        df_equity["drawdown_pct"] = df_equity["drawdown"] * 100
        
        # Calculate risk metrics using Risk Engine
        max_dd = calculate_max_drawdown(df_equity["portfolio_value"])
        volatility = calculate_volatility(df_equity["daily_return"])
        sharpe = calculate_sharpe_ratio(df_equity["daily_return"])
        sortino = calculate_sortino_ratio(df_equity["daily_return"])
        
        # Calculate CAGR (Annualized Return)
        num_days = len(df_equity)
        if num_days > 0:
            num_years = num_days / 365.0
            cagr = ((final_portfolio_value / starting_capital) ** (1.0 / num_years) - 1.0) * 100.0
        else:
            cagr = 0.0
            
        calmar = calculate_calmar_ratio(cagr, max_dd)
    else:
        max_dd = 0.0
        volatility = 0.0
        sharpe = 0.0
        sortino = 0.0
        cagr = 0.0
        calmar = 0.0

    if trades > 0:
        win_rate = (wins / trades) * 100
        average_trade = (total_return / trades)
    else:
        win_rate = 0
        average_trade = 0

    # Export logs to results/
    if export:
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        results_dir = os.path.join(project_root, "results")
        os.makedirs(results_dir, exist_ok=True)
        
        # Save trade log
        df_trades = pd.DataFrame(trade_log)
        df_trades.to_csv(os.path.join(results_dir, "trades.csv"), index=False)
        
        # Save equity curve
        df_equity.to_csv(os.path.join(results_dir, "equity_curve.csv"), index=True)
        
        # Plot and save curves
        plot_equity_curve(df_equity, strategy.name, starting_capital=starting_capital, save_path=os.path.join(results_dir, "equity_curve.png"))
        plot_drawdown_curve(df_equity, strategy.name, save_path=os.path.join(results_dir, "drawdown.png"))

    if verbose:
        print("=" * 60)
        print("Backtest Complete - Professional Risk & Performance Report")
        print("=" * 60)
        print()
        print(f"Strategy Name:                {strategy.name}")
        print(f"Trades Closed:                {trades}")
        print(f"Wins / Losses:                {wins} Wins / {losses} Losses")
        print(f"Win Rate:                     {win_rate:.2f}%")
        print(f"Average Trade Return:         {average_trade:.2f}%")
        print()
        print(f"Total Return (Sum):           {total_return:.2f}%")
        print(f"Portfolio Return (Comp):      {portfolio_return:.2f}%")
        print(f"Annualized Return (CAGR):     {cagr:.2f}%")
        print(f"Buy & Hold Return:            {buy_hold_return:.2f}%")
        print()
        print(f"Max Drawdown:                 {max_dd:.2f}%")
        print(f"Volatility (Annualized):      {volatility:.2f}%")
        print(f"Sharpe Ratio (R_f=0%):        {sharpe:.2f}")
        print(f"Sortino Ratio (R_f=0%):       {sortino:.2f}")
        print(f"Calmar Ratio:                 {calmar:.2f}")
        print()
        print(f"Starting Capital:             ${starting_capital:,.2f}")
        print(f"Final Capital:                ${final_portfolio_value:,.2f}")
        print()
        print("=" * 60)

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
        "cagr": cagr,
        "starting_capital": starting_capital,
        "final_capital": final_portfolio_value,
        "buy_hold_return": buy_hold_return,
        "max_drawdown": max_dd,
        "volatility": volatility,
        "sharpe": sharpe,
        "sortino": sortino,
        "calmar": calmar,
        "parameters": strategy.get_parameters(),
        "trade_log": trade_log,
        "equity_curve": df_equity
    }

if __name__ == "__main__":
    run_backtest()