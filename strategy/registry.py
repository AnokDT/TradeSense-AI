from strategy.ema_price_crossover import EMAPriceCrossoverStrategy
from strategy.ema_crossover import EMACrossoverStrategy
from strategy.sma_crossover import SMACrossoverStrategy
from strategy.macd_strategy import MACDStrategy
from strategy.supertrend_strategy import SupertrendStrategy
from strategy.donchian_breakout import DonchianBreakoutStrategy
from strategy.rsi_strategy import RSIStrategy
from strategy.bollinger_strategy import BollingerBandsStrategy
from strategy.atr_breakout import ATRBreakoutStrategy

STRATEGIES = {
    "ema_price": EMAPriceCrossoverStrategy,
    "ema_cross": EMACrossoverStrategy,
    "sma_cross": SMACrossoverStrategy,
    "macd": MACDStrategy,
    "supertrend": SupertrendStrategy,
    "donchian": DonchianBreakoutStrategy,
    "rsi": RSIStrategy,
    "bollinger": BollingerBandsStrategy,
    "atr_breakout": ATRBreakoutStrategy
}

def get_strategy_class(strategy_name: str):
    """
    Returns the strategy class matching the strategy name.
    """
    if strategy_name not in STRATEGIES:
        raise ValueError(f"Strategy {strategy_name} not found in registry. Available: {list(STRATEGIES.keys())}")
    return STRATEGIES[strategy_name]
