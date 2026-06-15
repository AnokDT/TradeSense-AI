import pandas as pd
from strategy.base import BaseStrategy

class BollingerBandsStrategy(BaseStrategy):
    """
    Bollinger Bands Strategy:
    - BUY when Close < Lower Band
    - SELL when Close > Upper Band
    """
    def __init__(self, period=20, std_dev=2.0):
        super().__init__(name=f"Bollinger Bands (Period {period}, Std {std_dev})")
        self.parameters = {
            "period": period,
            "std_dev": std_dev
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
            
        period = self.parameters["period"]
        std_dev = self.parameters["std_dev"]
        
        sma = close_prices.rolling(window=period).mean()
        std = close_prices.rolling(window=period).std()
        
        df["BB_upper"] = sma + std_dev * std
        df["BB_lower"] = sma - std_dev * std
        df["Close_clean"] = close_prices
        return df

    def generate_signal(self, data: pd.DataFrame, index: int) -> str:
        if index < 0 or index >= len(data):
            return "WAIT"
            
        row = data.iloc[index]
        close_val = row["Close_clean"]
        upper = row["BB_upper"]
        lower = row["BB_lower"]
        
        if pd.isna(upper) or pd.isna(lower) or pd.isna(close_val):
            return "WAIT"
            
        if close_val < lower:
            return "BUY"
        elif close_val > upper:
            return "SELL"
        else:
            return "WAIT"
