import unittest
import pandas as pd
import numpy as np
from backtesting.risk import (
    calculate_max_drawdown,
    calculate_volatility,
    calculate_sharpe_ratio,
    calculate_sortino_ratio,
    calculate_calmar_ratio
)

class TestRiskMetrics(unittest.TestCase):
    def test_max_drawdown(self):
        # Known series: 100 -> 120 -> 90 -> 110 -> 80 -> 120
        # Peaks:        100 -> 120 -> 120 -> 120 -> 120 -> 120
        # Drawdowns:    0   -> 0   -> -25%-> -8.3%-> -33.3% -> 0
        # Max drawdown should be 33.33333333333333 %
        equity = pd.Series([100.0, 120.0, 90.0, 110.0, 80.0, 120.0])
        max_dd = calculate_max_drawdown(equity)
        self.assertAlmostEqual(max_dd, 33.33333333, places=5)
        
        # Growing series: no drawdown
        growing = pd.Series([100, 101, 102, 103, 104])
        self.assertEqual(calculate_max_drawdown(growing), 0.0)

    def test_volatility(self):
        # Constant returns: volatility should be 0
        returns = pd.Series([0.01, 0.01, 0.01, 0.01])
        vol = calculate_volatility(returns, trading_days=365)
        self.assertEqual(vol, 0.0)
        
        # Hand-calculated daily returns: [0.01, -0.01, 0.02, -0.02]
        # Mean = 0.0
        # Variance (sample) = (0.01^2 + (-0.01)^2 + 0.02^2 + (-0.02)^2) / 3 = (0.0001 + 0.0001 + 0.0004 + 0.0004) / 3 = 0.0010 / 3 = 0.00033333
        # Std = sqrt(0.00033333) = 0.0182574
        # Annualized Volatility (365 days) = Std * sqrt(365) * 100 = 0.0182574 * 19.10497 * 100 = 34.8803%
        returns = pd.Series([0.01, -0.01, 0.02, -0.02])
        vol = calculate_volatility(returns, trading_days=365)
        self.assertAlmostEqual(vol, 34.8807492, places=5)

    def test_sharpe_ratio(self):
        # Mean = 0.001 (0.1%), Std = 0.01 (1%)
        # Daily Sharpe = 0.1
        # Annualized Sharpe (365 days) = 0.1 * sqrt(365) = 1.910497
        returns = pd.Series([0.011, -0.009, 0.011, -0.009]) # Mean = 0.001, Std = 0.011547
        # Let's use simpler mock series
        returns = pd.Series([0.02, 0.00, 0.02, 0.00]) # Mean = 0.01, Std = 0.011547
        # Daily Sharpe = 0.01 / 0.011547 = 0.866025
        # Annualized Sharpe (365) = 0.866025 * 19.10497 = 16.54538
        sharpe = calculate_sharpe_ratio(returns, trading_days=365)
        self.assertAlmostEqual(sharpe, 16.545392, places=5)

    def test_sortino_ratio(self):
        # Returns: [0.02, -0.01, 0.03, -0.02]
        # Mean = 0.005 (0.5%)
        # Negative returns: np.minimum(returns, 0) = [0, -0.01, 0, -0.02]
        # Downside variance = (0 + 0.0001 + 0 + 0.0004) / 4 = 0.000125
        # Downside deviation = sqrt(0.000125) = 0.0111803
        # Daily Sortino = 0.005 / 0.0111803 = 0.4472136
        # Annualized Sortino (365) = 0.4472136 * 19.10497 = 8.54400
        returns = pd.Series([0.02, -0.01, 0.03, -0.02])
        sortino = calculate_sortino_ratio(returns, trading_days=365)
        self.assertAlmostEqual(sortino, 8.5440037, places=5)

    def test_calmar_ratio(self):
        self.assertEqual(calculate_calmar_ratio(20.0, 10.0), 2.0)
        self.assertEqual(calculate_calmar_ratio(15.0, 0.0), 0.0)

if __name__ == "__main__":
    unittest.main()
