import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend to avoid window popping
import matplotlib.pyplot as plt

def plot_equity_curve(df_equity: pd.DataFrame, strategy_name: str, starting_capital: float = 10000.0, save_path: str = None):
    """
    Plots the strategy equity curve vs Buy & Hold benchmark.
    """
    if df_equity.empty or "portfolio_value" not in df_equity.columns or "price" not in df_equity.columns:
        print("Empty or invalid equity curve data. Skipping equity plot.")
        return
        
    first_price = df_equity["price"].iloc[0]
    df_equity_copy = df_equity.copy()
    df_equity_copy["bh_value"] = (df_equity_copy["price"] / first_price) * starting_capital
    
    plt.figure(figsize=(12, 6))
    plt.plot(df_equity_copy.index, df_equity_copy["portfolio_value"], label=f"TradeSense ({strategy_name})", color="#00C805", linewidth=2)
    plt.plot(df_equity_copy.index, df_equity_copy["bh_value"], label="Buy & Hold Benchmark", color="#7C8B9E", linestyle="--", linewidth=1.5)
    
    plt.title(f"Equity Curve - {strategy_name} vs Buy & Hold", fontsize=14, fontweight="bold", pad=15)
    plt.xlabel("Date", fontsize=11, labelpad=10)
    plt.ylabel("Portfolio Value ($)", fontsize=11, labelpad=10)
    plt.grid(True, linestyle=":", alpha=0.6)
    plt.legend(frameon=True, facecolor="white", edgecolor="none")
    plt.tight_layout()
    
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=300)
        print(f"Equity curve chart saved to: {save_path}")
    plt.close()

def plot_drawdown_curve(df_equity: pd.DataFrame, strategy_name: str, save_path: str = None):
    """
    Plots the daily drawdown percentage curve.
    """
    if df_equity.empty or "drawdown_pct" not in df_equity.columns:
        print("Empty or invalid equity curve data. Skipping drawdown plot.")
        return
        
    plt.figure(figsize=(12, 4))
    plt.fill_between(df_equity.index, df_equity["drawdown_pct"], 0, color="#FF3B30", alpha=0.25, label="Drawdown %")
    plt.plot(df_equity.index, df_equity["drawdown_pct"], color="#FF3B30", linewidth=1.5)
    
    plt.title(f"Drawdown Profile - {strategy_name}", fontsize=12, fontweight="bold", pad=15)
    plt.xlabel("Date", fontsize=10)
    plt.ylabel("Drawdown (%)", fontsize=10)
    plt.ylim(bottom=min(-5.0, df_equity["drawdown_pct"].min() * 1.1), top=1.0)
    plt.grid(True, linestyle=":", alpha=0.6)
    plt.tight_layout()
    
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=300)
        print(f"Drawdown chart saved to: {save_path}")
    plt.close()

def plot_optimization_results(df_opt: pd.DataFrame, param_cols: list, metric_col: str = "portfolio_return_pct", save_path: str = None):
    """
    Plots optimization tuning results as either a 1D chart or a 2D heatmap.
    """
    if df_opt.empty or not all(c in df_opt.columns for c in param_cols + [metric_col]):
        print("Invalid optimization data for plotting. Skipping plot.")
        return
        
    if len(param_cols) == 1:
        # 1D line chart
        df_sorted = df_opt.sort_values(by=param_cols[0])
        plt.figure(figsize=(10, 5))
        plt.plot(df_sorted[param_cols[0]], df_sorted[metric_col], marker="o", color="#007AFF", linewidth=2)
        plt.title(f"Parameter Tuning - Return vs {param_cols[0]}", fontsize=12, fontweight="bold", pad=15)
        plt.xlabel(param_cols[0])
        plt.ylabel("Portfolio Return (%)")
        plt.grid(True, linestyle=":", alpha=0.6)
        plt.tight_layout()
        if save_path:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            plt.savefig(save_path, dpi=300)
            print(f"Optimization tuning chart saved to: {save_path}")
        plt.close()
        
    elif len(param_cols) == 2:
        # 2D Heatmap
        try:
            # Pivot table
            pivot = df_opt.pivot(index=param_cols[0], columns=param_cols[1], values=metric_col)
            
            plt.figure(figsize=(10, 8))
            im = plt.imshow(pivot.values, cmap="RdYlGn", aspect="auto")
            plt.colorbar(im, label="Portfolio Return (%)")
            
            plt.xticks(np.arange(len(pivot.columns)), pivot.columns)
            plt.yticks(np.arange(len(pivot.index)), pivot.index)
            
            plt.xlabel(param_cols[1])
            plt.ylabel(param_cols[0])
            plt.title(f"Optimization Heatmap - {param_cols[0]} vs {param_cols[1]}", fontsize=12, fontweight="bold", pad=15)
            
            # Write labels in cells
            for y in range(pivot.shape[0]):
                for x in range(pivot.shape[1]):
                    val = pivot.values[y, x]
                    plt.text(x, y, f"{val:.1f}%", ha="center", va="center", 
                             color="black" if 20 < val < 150 else ("white" if val >= 150 else "black"), fontsize=9)
                    
            plt.tight_layout()
            if save_path:
                os.makedirs(os.path.dirname(save_path), exist_ok=True)
                plt.savefig(save_path, dpi=300)
                print(f"Optimization heatmap saved to: {save_path}")
            plt.close()
        except Exception as e:
            print(f"Failed to generate 2D optimization heatmap: {e}")
