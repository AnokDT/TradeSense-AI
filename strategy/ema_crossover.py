import pandas as pd
from strategy.base import BaseStrategy
from indicators.ema import calculate_ema

class EMACrossoverStrategy(BaseStrategy):
    """
    EMA Fast vs EMA Slow Crossover Strategy:
    - BUY when EMA_fast > EMA_slow
    - SELL when EMA_fast <= EMA_slow
    """
    def __init__(self, fast_period=50, slow_period=200):
        super().__init__(name=f"EMA Crossover (EMA {fast_period} vs EMA {slow_period})")
        self.parameters = {
            "fast_period": fast_period,
            "slow_period": slow_period
        }

    def prepare_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        df = data.copy()
        
        # Flatten MultiIndex columns if present
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [col[0] for col in df.columns]
            
        if "Close" in df.columns:
            close_prices = df["Close"]
        else:
            close_prices = df.iloc[:, 0]
            
        fast_period = self.parameters["fast_period"]
        slow_period = self.parameters["slow_period"]
        
        df["EMA_fast"] = calculate_ema(close_prices, fast_period)
        df["EMA_slow"] = calculate_ema(close_prices, slow_period)
        df["Close_clean"] = close_prices
        return df

    def generate_signal(self, data: pd.DataFrame, index: int) -> str:
        if index < 0 or index >= len(data):
            return "WAIT"
            
        row = data.iloc[index]
        ema_fast = row["EMA_fast"]
        ema_slow = row["EMA_slow"]
        
        if pd.isna(ema_fast) or pd.isna(ema_slow):
            return "WAIT"
            
        if ema_fast > ema_slow:
            return "BUY"
        else:
            return "SELL"
