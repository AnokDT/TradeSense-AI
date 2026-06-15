import os
import json
import pandas as pd
from research.experiment import Experiment

# File paths
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(PROJECT_ROOT, "results")
DB_JSON_PATH = os.path.join(RESULTS_DIR, "research_database.json")
DB_CSV_PATH = os.path.join(RESULTS_DIR, "research_database.csv")

def ensure_results_dir():
    os.makedirs(RESULTS_DIR, exist_ok=True)

def load_database() -> list:
    """
    Loads all experiments from the JSON database.
    Returns a list of Experiment objects.
    """
    if not os.path.exists(DB_JSON_PATH):
        return []
    try:
        with open(DB_JSON_PATH, "r") as f:
            data = json.load(f)
            return [Experiment.from_dict(d) for d in data]
    except Exception as e:
        print(f"Error loading research database: {e}")
        return []

def save_database(experiments: list):
    """
    Saves the list of Experiment objects to the JSON database.
    Also automatically exports the database to CSV.
    """
    ensure_results_dir()
    try:
        # Convert to dictionary representation
        dict_list = [exp.to_dict() for exp in experiments]
        with open(DB_JSON_PATH, "w") as f:
            json.dump(dict_list, f, indent=2)
            
        # Export to CSV
        df = pd.DataFrame(dict_list)
        if not df.empty:
            df.to_csv(DB_CSV_PATH, index=False)
    except Exception as e:
        print(f"Error saving research database: {e}")

def add_experiment(experiment: Experiment):
    """
    Adds a new experiment to the database.
    If an experiment with the same strategy, parameters, symbol, and dates already exists,
    it updates the existing entry to avoid duplicates.
    """
    experiments = load_database()
    
    # Check for duplicate
    duplicate_idx = -1
    for idx, exp in enumerate(experiments):
        if (
            exp.strategy_name == experiment.strategy_name and
            exp.parameters == experiment.parameters and
            exp.symbol == experiment.symbol and
            exp.start_date == experiment.start_date and
            exp.end_date == experiment.end_date
        ):
            duplicate_idx = idx
            break
            
    if duplicate_idx != -1:
        # Update existing
        experiments[duplicate_idx] = experiment
    else:
        # Append new
        experiments.append(experiment)
        
    save_database(experiments)
