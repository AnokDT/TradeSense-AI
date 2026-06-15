import pandas as pd
from strategy.base import BaseStrategy

class DonchianBreakoutStrategy(BaseStrategy):
    """
    Donchian Breakout Strategy:
    - BUY when Close > Donchian Upper Band (Highest High over lookback)
    - SELL when Close < Donchian Lower Band (Lowest Low over lookback)
    """
    def __init__(self, lookback_period=20):
        super().__init__(name=f"Donchian Breakout (Lookback {lookback_period})")
        self.parameters = {
            "lookback_period": lookback_period
        }

    def prepare_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        df = data.copy()
        
        # Flatten MultiIndex columns if present
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [col[0] for col in df.columns]
            
        high = df["High"]
        low = df["Low"]
        close = df["Close"]
        
        lookback = self.parameters["lookback_period"]
        
        # Exclude the current candle's high/low by using .shift(1)
        df["Donchian_upper"] = high.shift(1).rolling(window=lookback).max()
        df["Donchian_lower"] = low.shift(1).rolling(window=lookback).min()
        df["Close_clean"] = close
        return df

    def generate_signal(self, data: pd.DataFrame, index: int) -> str:
        if index < 0 or index >= len(data):
            return "WAIT"
            
        row = data.iloc[index]
        close_val = row["Close_clean"]
        upper = row["Donchian_upper"]
        lower = row["Donchian_lower"]
        
        if pd.isna(upper) or pd.isna(lower) or pd.isna(close_val):
            return "WAIT"
            
        if close_val > upper:
            return "BUY"
        elif close_val < lower:
            return "SELL"
        else:
            # Maintain position or wait
            return "WAIT"
