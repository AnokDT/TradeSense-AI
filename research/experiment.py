from datetime import datetime

class Experiment:
    """
    Data model representing a completed quantitative backtesting or optimization experiment.
    """
    def __init__(
        self,
        strategy_name: str,
        parameters: dict,
        portfolio_return: float,
        sharpe: float,
        sortino: float,
        max_drawdown: float,
        robustness: float,
        walk_forward_score: float = 0.0,
        composite_score: float = 0.0,
        symbol: str = "BTC-USD",
        start_date: str = "",
        end_date: str = "",
        timestamp: str = None
    ):
        self.strategy_name = strategy_name
        self.parameters = parameters
        self.portfolio_return = float(portfolio_return)
        self.sharpe = float(sharpe)
        self.sortino = float(sortino)
        self.max_drawdown = float(max_drawdown)
        self.robustness = float(robustness)
        self.walk_forward_score = float(walk_forward_score)
        self.composite_score = float(composite_score)
        self.symbol = symbol
        self.start_date = start_date
        self.end_date = end_date
        self.timestamp = timestamp or datetime.now().isoformat()

    def to_dict(self) -> dict:
        """
        Converts the Experiment object to a dictionary.
        """
        return {
            "strategy_name": self.strategy_name,
            "parameters": self.parameters,
            "return": self.portfolio_return,
            "sharpe": self.sharpe,
            "sortino": self.sortino,
            "drawdown": self.max_drawdown,
            "robustness": self.robustness,
            "walk_forward_score": self.walk_forward_score,
            "composite_score": self.composite_score,
            "symbol": self.symbol,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "timestamp": self.timestamp
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Experiment':
        """
        Instantiates an Experiment object from a dictionary.
        """
        return cls(
            strategy_name=data["strategy_name"],
            parameters=data["parameters"],
            portfolio_return=data["return"],
            sharpe=data["sharpe"],
            sortino=data["sortino"],
            max_drawdown=data["drawdown"],
            robustness=data["robustness"],
            walk_forward_score=data.get("walk_forward_score", 0.0),
            composite_score=data.get("composite_score", 0.0),
            symbol=data.get("symbol", "BTC-USD"),
            start_date=data.get("start_date", ""),
            end_date=data.get("end_date", ""),
            timestamp=data.get("timestamp")
        )
