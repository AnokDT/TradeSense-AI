import unittest
import os
import pandas as pd
from strategy.registry import STRATEGIES, get_strategy_class
from research.experiment import Experiment

# Override database path for testing to avoid contaminating production database
import research.database
research.database.DB_JSON_PATH = os.path.join(research.database.RESULTS_DIR, "test_research_database.json")
research.database.DB_CSV_PATH = os.path.join(research.database.RESULTS_DIR, "test_research_database.csv")

from research.database import add_experiment, load_database
from research.query import get_best_strategy, get_best_strategy_by_metric


class TestResearchPlatform(unittest.TestCase):
    def test_registry(self):
        # Verify all strategies are in the registry and can be instantiated with default params
        for name, cls in STRATEGIES.items():
            strategy = cls()
            self.assertIsNotNone(strategy.name)
            self.assertEqual(get_strategy_class(name), cls)

    def test_database_and_query(self):
        # Create a mock experiment
        exp1 = Experiment(
            strategy_name="EMA Price Crossover (Mock)",
            parameters={"ema_period": 50},
            portfolio_return=150.0,
            sharpe=1.2,
            sortino=1.5,
            max_drawdown=20.0,
            robustness=85.0,
            walk_forward_score=66.6,
            composite_score=75.0,
            symbol="BTC-USD",
            start_date="2021-06-15",
            end_date="2026-06-15"
        )
        
        # Save to DB
        add_experiment(exp1)
        
        # Load and verify
        db = load_database()
        self.assertTrue(len(db) > 0)
        
        # Verify duplicate handler (adding same parameters again should not increase length)
        initial_len = len(db)
        add_experiment(exp1)
        new_db = load_database()
        self.assertEqual(len(new_db), initial_len)
        
        # Test Query Engine
        best = get_best_strategy()
        self.assertIsNotNone(best)
        
        best_sharpe = get_best_strategy_by_metric("sharpe")
        self.assertEqual(best_sharpe["strategy_name"], "EMA Price Crossover (Mock)")

    @classmethod
    def tearDownClass(cls):
        # Clean up test database files
        for path in [research.database.DB_JSON_PATH, research.database.DB_CSV_PATH]:
            if os.path.exists(path):
                try:
                    os.remove(path)
                except Exception as e:
                    print(f"Error cleaning up test file {path}: {e}")

if __name__ == "__main__":
    unittest.main()

