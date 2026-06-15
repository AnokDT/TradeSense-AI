def calculate_composite_score(portfolio_return: float, max_drawdown: float, sharpe: float, robustness: float) -> float:
    """
    Calculates a composite score (0 to 100) for a strategy based on:
    - Return Score (35% weight)
    - Drawdown Score (25% weight)
    - Sharpe Score (20% weight)
    - Robustness Score (20% weight)
    
    Formula:
    Score = 0.35 * return_score + 0.25 * drawdown_score + 0.20 * sharpe_score + 0.20 * robustness_score
    """
    # 1. Return Score: Capped at 100% total return for perfect 100 points
    return_score = min(100.0, max(0.0, portfolio_return))
    
    # 2. Drawdown Score: Higher score for lower drawdown (100 - MDD%)
    drawdown_score = max(0.0, 100.0 - max_drawdown)
    
    # 3. Sharpe Score: Capped at 3.0 Sharpe ratio for perfect 100 points
    sharpe_score = min(100.0, max(0.0, (sharpe / 3.0) * 100.0))
    
    # 4. Robustness Score: Already 0 to 100
    robustness_score = min(100.0, max(0.0, robustness))
    
    # Weighted composite score
    composite = (
        0.35 * return_score +
        0.25 * drawdown_score +
        0.20 * sharpe_score +
        0.20 * robustness_score
    )
    
    return float(composite)

def rank_strategies_composite(strategies_results: list) -> list:
    """
    Ranks a list of strategy backtest results based on the composite score.
    Each item in strategies_results should be a dictionary with:
    - 'strategy_name'
    - 'portfolio_return'
    - 'max_drawdown'
    - 'sharpe'
    - 'robustness' (optional, defaults to 50 if missing)
    """
    ranked_list = []
    
    for res in strategies_results:
        rob = res.get("robustness", 50.0)
        score = calculate_composite_score(
            portfolio_return=res["portfolio_return"],
            max_drawdown=res["max_drawdown"],
            sharpe=res["sharpe"],
            robustness=rob
        )
        
        ranked_res = res.copy()
        ranked_res["composite_score"] = round(score, 2)
        ranked_list.append(ranked_res)
        
    # Sort by composite_score descending
    ranked_list = sorted(ranked_list, key=lambda x: x["composite_score"], reverse=True)
    return ranked_list
