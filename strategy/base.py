import pandas as pd

class BaseStrategy:
    """
    Abstract base class for all TradeSense trading strategies.
    """
    def __init__(self, name="Base Strategy"):
        self.name = name
        self.parameters = {}

    def prepare_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Pre-calculate all necessary indicators for the dataset.
        Returns a new DataFrame (or a copy) with the indicator columns added.
        """
        raise NotImplementedError("Subclasses must implement prepare_indicators")

    def generate_signal(self, data: pd.DataFrame, index: int) -> str:
        """
        Generate a trade signal ("BUY", "SELL", or "WAIT") at a specific row index.
        """
        raise NotImplementedError("Subclasses must implement generate_signal")

    def get_parameters(self) -> dict:
        """
        Get the current parameters of the strategy.
        """
        return self.parameters

    def set_parameters(self, **params):
        """
        Set or update parameters of the strategy.
        """
        for key, val in params.items():
            if key in self.parameters:
                self.parameters[key] = val
            else:
                raise ValueError(f"Unknown parameter: {key} for strategy {self.name}")
