import pandas as pd
from strategy.base import BaseStrategy

class SMACrossoverStrategy(BaseStrategy):
    """
    SMA Fast vs SMA Slow Crossover Strategy:
    - BUY when SMA_fast > SMA_slow
    - SELL when SMA_fast <= SMA_slow
    """
    def __init__(self, fast_period=20, slow_period=50):
        super().__init__(name=f"SMA Crossover (SMA {fast_period} vs SMA {slow_period})")
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
        
        df["SMA_fast"] = close_prices.rolling(window=fast_period).mean()
        df["SMA_slow"] = close_prices.rolling(window=slow_period).mean()
        df["Close_clean"] = close_prices
        return df

    def generate_signal(self, data: pd.DataFrame, index: int) -> str:
        if index < 0 or index >= len(data):
            return "WAIT"
            
        row = data.iloc[index]
        sma_fast = row["SMA_fast"]
        sma_slow = row["SMA_slow"]
        
        if pd.isna(sma_fast) or pd.isna(sma_slow):
            return "WAIT"
            
        if sma_fast > sma_slow:
            return "BUY"
        else:
            return "SELL"
