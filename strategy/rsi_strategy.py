import pandas as pd
from strategy.base import BaseStrategy
from indicators.rsi import calculate_rsi

class RSIStrategy(BaseStrategy):
    """
    RSI Reversal Strategy:
    - BUY when RSI < oversold (default: 30)
    - SELL when RSI > overbought (default: 70)
    """
    def __init__(self, rsi_period=14, oversold=30, overbought=70):
        super().__init__(name=f"RSI Strategy (RSI {rsi_period}, OS {oversold}, OB {overbought})")
        self.parameters = {
            "rsi_period": rsi_period,
            "oversold": oversold,
            "overbought": overbought
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
            
        rsi_period = self.parameters["rsi_period"]
        df["RSI"] = calculate_rsi(close_prices, period=rsi_period)
        df["Close_clean"] = close_prices
        return df

    def generate_signal(self, data: pd.DataFrame, index: int) -> str:
        if index < 0 or index >= len(data):
            return "WAIT"
            
        row = data.iloc[index]
        rsi_val = row["RSI"]
        
        if pd.isna(rsi_val):
            return "WAIT"
            
        oversold = self.parameters["oversold"]
        overbought = self.parameters["overbought"]
        
        if rsi_val < oversold:
            return "BUY"
        elif rsi_val > overbought:
            return "SELL"
        else:
            return "WAIT"
