import pandas as pd
from strategy.base import BaseStrategy
from indicators.ema import calculate_ema

class EMAPriceCrossoverStrategy(BaseStrategy):
    """
    EMA Price Crossover Strategy:
    - BUY when Price > EMA(period)
    - SELL when Price <= EMA(period)
    """
    def __init__(self, ema_period=50):
        super().__init__(name=f"EMA Price Crossover (EMA {ema_period})")
        self.parameters = {"ema_period": ema_period}

    def prepare_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        df = data.copy()
        
        # Flatten MultiIndex columns if present
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [col[0] for col in df.columns]
            
        if "Close" in df.columns:
            close_prices = df["Close"]
        else:
            close_prices = df.iloc[:, 0]
            
        period = self.parameters["ema_period"]
        df["EMA_indicator"] = calculate_ema(close_prices, period)
        df["Close_clean"] = close_prices
        return df

    def generate_signal(self, data: pd.DataFrame, index: int) -> str:
        # Avoid out of bounds or NaN
        if index < 0 or index >= len(data):
            return "WAIT"
            
        row = data.iloc[index]
        close_val = row["Close_clean"]
        ema_val = row["EMA_indicator"]
        
        if pd.isna(ema_val) or pd.isna(close_val):
            return "WAIT"
            
        if close_val > ema_val:
            return "BUY"
        else:
            return "SELL"
