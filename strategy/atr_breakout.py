import pandas as pd
from strategy.base import BaseStrategy

class ATRBreakoutStrategy(BaseStrategy):
    """
    ATR Breakout Strategy:
    - BUY when Close > Middle + multiplier * ATR
    - SELL when Close < Middle - multiplier * ATR
    """
    def __init__(self, atr_period=14, multiplier=1.5):
        super().__init__(name=f"ATR Breakout (ATR {atr_period}, Mult {multiplier})")
        self.parameters = {
            "atr_period": atr_period,
            "multiplier": multiplier
        }

    def prepare_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        df = data.copy()
        
        # Flatten MultiIndex columns if present
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [col[0] for col in df.columns]
            
        high = df["High"]
        low = df["Low"]
        close = df["Close"]
        
        atr_period = self.parameters["atr_period"]
        multiplier = self.parameters["multiplier"]
        
        # Calculate True Range (TR)
        prev_close = close.shift(1)
        tr1 = high - low
        tr2 = abs(high - prev_close)
        tr3 = abs(low - prev_close)
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=atr_period).mean()
        
        sma = close.rolling(window=atr_period).mean()
        
        df["ATR_upper"] = sma + multiplier * atr
        df["ATR_lower"] = sma - multiplier * atr
        df["Close_clean"] = close
        return df

    def generate_signal(self, data: pd.DataFrame, index: int) -> str:
        if index < 0 or index >= len(data):
            return "WAIT"
            
        row = data.iloc[index]
        close_val = row["Close_clean"]
        upper = row["ATR_upper"]
        lower = row["ATR_lower"]
        
        if pd.isna(upper) or pd.isna(lower) or pd.isna(close_val):
            return "WAIT"
            
        if close_val > upper:
            return "BUY"
        elif close_val < lower:
            return "SELL"
        else:
            return "WAIT"
