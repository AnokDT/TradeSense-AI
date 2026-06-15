import pandas as pd
from strategy.base import BaseStrategy
from indicators.ema import calculate_ema

class MACDStrategy(BaseStrategy):
    """
    MACD Strategy:
    - BUY when MACD > Signal Line
    - SELL when MACD <= Signal Line
    """
    def __init__(self, fast_period=12, slow_period=26, signal_period=9):
        super().__init__(name=f"MACD Strategy (MACD {fast_period}/{slow_period}/{signal_period})")
        self.parameters = {
            "fast_period": fast_period,
            "slow_period": slow_period,
            "signal_period": signal_period
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
            
        fast = self.parameters["fast_period"]
        slow = self.parameters["slow_period"]
        sig = self.parameters["signal_period"]
        
        fast_ema = calculate_ema(close_prices, fast)
        slow_ema = calculate_ema(close_prices, slow)
        
        df["MACD_line"] = fast_ema - slow_ema
        df["MACD_signal"] = calculate_ema(df["MACD_line"], sig)
        df["Close_clean"] = close_prices
        return df

    def generate_signal(self, data: pd.DataFrame, index: int) -> str:
        if index < 0 or index >= len(data):
            return "WAIT"
            
        row = data.iloc[index]
        macd = row["MACD_line"]
        signal = row["MACD_signal"]
        
        if pd.isna(macd) or pd.isna(signal):
            return "WAIT"
            
        if macd > signal:
            return "BUY"
        else:
            return "SELL"
