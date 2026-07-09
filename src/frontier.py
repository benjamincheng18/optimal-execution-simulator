import numpy as np
import pandas as pd
import plotly.graph_objects as go
from src.almgren_chriss import almgren_chriss_trajectory
from src.simulator import monte_carlo_simulation

def frontier_construction(X, T, N, sigma, eta, gamma, lambda_range, n_sims, S0):
    """
    Sweep lambda, compute AC trajectory + Monte Carlo cost distribution for each,
    collect (lambda, mean_cost, variance_cost) into a DataFrame.
    
    Parameters
    ----------
    X, T, N, sigma, eta, gamma : fixed AC model parameters
    lambda_range : array-like, risk-aversion values to sweep
    n_sims : int, Monte Carlo simulations per lambda
    S0 : float, arrival price
    
    Returns
    -------
    pd.DataFrame with columns: lambda, mean_cost, variance_cost
    """
    results = []
    
    for lam in lambda_range:
        trajectory = almgren_chriss_trajectory(X, T, N, lam, sigma, eta, gamma)
        
        shares_traded = trajectory["shares_traded"].dropna().values
        
        IS_raw, IS_paired = monte_carlo_simulation(S0, shares_traded, sigma, eta, gamma, T/N, n_sims)
        mean_cost = IS_paired['IS_paired'].mean()
        variance_cost = IS_raw['IS_raw'].var()
        
        results.append((lam, mean_cost, variance_cost))
    
    return pd.DataFrame(results, columns=['lambda', 'mean_cost', 'variance_cost'])


def frontier_plot(frontier):
    """
    Plot the efficient frontier: mean_cost (x) vs variance_cost (y).
    
    Parameters
    ----------
    frontier : pd.DataFrame, output of frontier_construction
    """
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=frontier['mean_cost'],
        y=frontier['variance_cost'],
        mode='lines+markers',
        text=frontier['lambda'],
        hovertemplate='λ=%{text}<br>Mean Cost=%{x}<br>Variance=%{y}'
    ))
    fig.update_layout(
        title='Execution Efficient Frontier',
        xaxis_title='Mean Implementation Shortfall ($)',
        yaxis_title='Variance of Implementation Shortfall'
    )
    return fig