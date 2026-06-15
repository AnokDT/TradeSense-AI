from research.database import load_database

def get_all_experiments() -> list:
    """
    Returns all experiments currently in the database as dictionaries.
    """
    return [exp.to_dict() for exp in load_database()]

def get_best_strategy() -> dict:
    """
    Returns the experiment with the highest composite score.
    """
    experiments = get_all_experiments()
    if not experiments:
        return {}
    # Sort by composite_score descending
    sorted_exps = sorted(experiments, key=lambda x: x.get("composite_score", 0.0), reverse=True)
    return sorted_exps[0]

def get_top_n_strategies(n: int) -> list:
    """
    Returns the top N experiments ranked by composite score.
    """
    experiments = get_all_experiments()
    if not experiments:
        return []
    sorted_exps = sorted(experiments, key=lambda x: x.get("composite_score", 0.0), reverse=True)
    return sorted_exps[:n]

def get_best_strategy_by_metric(metric: str) -> dict:
    """
    Returns the best strategy experiment based on a specific metric.
    Metrics supported: 'return', 'sharpe', 'sortino', 'drawdown', 'robustness', 'walk_forward_score', 'composite_score'.
    For 'drawdown', it minimizes (lower is better); for others, it maximizes.
    """
    experiments = get_all_experiments()
    if not experiments:
        return {}
        
    valid_metrics = ['return', 'sharpe', 'sortino', 'drawdown', 'robustness', 'walk_forward_score', 'composite_score']
    if metric not in valid_metrics:
        raise ValueError(f"Invalid metric: '{metric}'. Supported metrics: {valid_metrics}")
        
    if metric == 'drawdown':
        # Sort ascending (lower drawdown is better)
        # Exclude experiments with 0 trades or invalid drawdowns if any
        sorted_exps = sorted(experiments, key=lambda x: x.get("drawdown", 100.0))
    else:
        # Sort descending (higher is better)
        sorted_exps = sorted(experiments, key=lambda x: x.get(metric, -999999.0), reverse=True)
        
    return sorted_exps[0] if sorted_exps else {}

def get_most_robust_strategy() -> dict:
    """
    Returns the strategy with the highest parameter robustness score.
    """
    return get_best_strategy_by_metric("robustness")

def get_best_walk_forward_strategy() -> dict:
    """
    Returns the strategy with the highest walk-forward score.
    """
    return get_best_strategy_by_metric("walk_forward_score")
