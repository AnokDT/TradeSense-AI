import pandas as pd
import numpy as np

def calculate_max_drawdown(equity_series: pd.Series) -> float:
    """
    Calculates the maximum drawdown of the equity curve as a positive percentage.
    Example: 15.5 meaning 15.5% max drawdown.
    """
    if len(equity_series) <= 1:
        return 0.0
    
    peaks = equity_series.cummax()
    drawdowns = (equity_series - peaks) / peaks
    max_dd = drawdowns.min()
    return float(abs(max_dd) * 100)

def calculate_volatility(daily_returns: pd.Series, trading_days: int = 365) -> float:
    """
    Calculates the annualized volatility of daily returns as a percentage.
    """
    if len(daily_returns) <= 1:
        return 0.0
    
    daily_std = daily_returns.std()
    if pd.isna(daily_std):
        return 0.0
        
    ann_vol = daily_std * np.sqrt(trading_days)
    return float(ann_vol * 100)

def calculate_sharpe_ratio(daily_returns: pd.Series, risk_free_rate: float = 0.0, trading_days: int = 365) -> float:
    """
    Calculates the annualized Sharpe ratio of daily returns.
    """
    if len(daily_returns) <= 1:
        return 0.0
        
    daily_rf = risk_free_rate / trading_days
    excess_returns = daily_returns - daily_rf
    
    mean_excess = excess_returns.mean()
    std_excess = excess_returns.std()
    
    if pd.isna(std_excess) or std_excess == 0:
        return 0.0
        
    daily_sharpe = mean_excess / std_excess
    ann_sharpe = daily_sharpe * np.sqrt(trading_days)
    return float(ann_sharpe)

def calculate_sortino_ratio(daily_returns: pd.Series, risk_free_rate: float = 0.0, trading_days: int = 365) -> float:
    """
    Calculates the annualized Sortino ratio of daily returns.
    Uses downside deviation (semi-standard deviation of negative excess returns).
    """
    if len(daily_returns) <= 1:
        return 0.0
        
    daily_rf = risk_free_rate / trading_days
    excess_returns = daily_returns - daily_rf
    
    mean_excess = excess_returns.mean()
    
    # Downside deviation: standard deviation of negative excess returns,
    # dividing by total length N (industry standard)
    negative_returns = np.minimum(excess_returns, 0)
    downside_variance = np.mean(negative_returns ** 2)
    downside_deviation = np.sqrt(downside_variance)
    
    if downside_deviation == 0:
        return 0.0
        
    daily_sortino = mean_excess / downside_deviation
    ann_sortino = daily_sortino * np.sqrt(trading_days)
    return float(ann_sortino)

def calculate_calmar_ratio(annualized_return: float, max_drawdown: float) -> float:
    """
    Calculates the Calmar ratio.
    Calmar = Annualized Return (%) / Max Drawdown (%)
    """
    if max_drawdown <= 0:
        return 0.0
    return float(annualized_return / max_drawdown)
