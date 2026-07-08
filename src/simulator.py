import numpy as np
import pandas as pd

def simulate_one_path(S0, shares_traded, sigma, eta, gamma, tau):
    """
    Simulate one realized execution path and compute implementation shortfall.
    
    Parameters
    ----------
    S0 : float, arrival price (mid-price at t=0)
    shares_traded : np.array, shares traded each period (from AC trajectory, excluding the NaN at k=0)
    sigma : float, volatility per unit time
    eta : float, temporary impact parameter
    gamma : float, permanent impact parameter
    tau : float, length of one interval
    
    Returns
    -------
    IS : float, total implementation shortfall in dollars for this simulated path
    """
    n_periods = len(shares_traded)
    
    shocks = np.random.normal(size=n_periods)
    
    mid_price = np.zeros(n_periods)
    for k in range(n_periods):
        if k == 0:
            mid_price[k] = S0
        else:
            mid_price[k] = mid_price[k-1] + sigma*np.sqrt(tau)*shocks[k] - gamma*shares_traded[k]
            

    execution_price = mid_price - eta * (shares_traded / tau)

    IS = np.sum((S0 - execution_price) * shares_traded)
    
    return IS


def monte_carlo_simulation(S0, shares_traded, sigma, eta, gamma, tau, n_sims):
    """
    Run simulate_one_path n_sims times and collect implementation shortfall results.
    
    Returns
    -------
    pd.DataFrame with one column 'IS', one row per simulation
    """
    # TODO: loop n_sims times, call simulate_one_path each time, collect results
    # results = ...
    results = []
    for i in range(n_sims):
        IS = simulate_one_path(S0, shares_traded, sigma, eta, gamma, tau)
        results.append(IS)

    return pd.DataFrame({'IS': results})