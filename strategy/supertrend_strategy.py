import pandas as pd
import numpy as np
from strategy.base import BaseStrategy

class SupertrendStrategy(BaseStrategy):
    """
    Supertrend Strategy:
    - BUY when trend flips bullish (1)
    - SELL when trend flips bearish (-1)
    """
    def __init__(self, atr_period=10, multiplier=3.0):
        super().__init__(name=f"Supertrend (ATR {atr_period}, Mult {multiplier})")
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
        
        hl2 = (high + low) / 2
        basic_upper = hl2 + multiplier * atr
        basic_lower = hl2 - multiplier * atr
        
        upper_band = list(basic_upper)
        lower_band = list(basic_lower)
        trend = [1] * len(df)
        close_list = list(close)
        
        # Supertrend calculation loop
        for i in range(1, len(df)):
            if pd.isna(atr.iloc[i]):
                continue
                
            # Previous state
            prev_trend = trend[i-1]
            prev_upper = upper_band[i-1]
            prev_lower = lower_band[i-1]
            
            # Lower band calculation
            if prev_trend == 1:
                lower_band[i] = max(basic_lower.iloc[i], prev_lower)
            else:
                lower_band[i] = basic_lower.iloc[i]
                
            # Upper band calculation
            if prev_trend == -1:
                upper_band[i] = min(basic_upper.iloc[i], prev_upper)
            else:
                upper_band[i] = basic_upper.iloc[i]
                
            # Trend determination
            if close_list[i] > upper_band[i]:
                trend[i] = 1
            elif close_list[i] < lower_band[i]:
                trend[i] = -1
            else:
                trend[i] = prev_trend
                # Standard adjustment
                if trend[i] == 1:
                    upper_band[i] = basic_upper.iloc[i]
                else:
                    lower_band[i] = basic_lower.iloc[i]
                    
        df["Supertrend_direction"] = trend
        df["Close_clean"] = close
        return df

    def generate_signal(self, data: pd.DataFrame, index: int) -> str:
        if index < 0 or index >= len(data):
            return "WAIT"
            
        row = data.iloc[index]
        direction = row["Supertrend_direction"]
        
        if pd.isna(direction):
            return "WAIT"
            
        if direction == 1:
            return "BUY"
        else:
            return "SELL"
