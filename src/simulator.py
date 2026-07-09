import numpy as np
import pandas as pd

def simulate_one_path(S0, shares_traded, sigma, eta, gamma, tau, eps):
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
    mid_price = np.zeros(n_periods)
    for k in range(n_periods):
        if k == 0:
            mid_price[k] = S0
        else:
            mid_price[k] = mid_price[k-1] + sigma*np.sqrt(tau)*eps[k] - gamma*shares_traded[k]
            

    execution_price = mid_price - eta * (shares_traded / tau)

    IS = np.sum((S0 - execution_price) * shares_traded)
    
    return IS


def monte_carlo_simulation(S0, shares_traded, sigma, eta, gamma, tau, n_sims):
    """
    Run Monte Carlo simulation with antithetic variates.
    
    Parameters
    ----------
    S0 : float, arrival price
    shares_traded : np.array, shares traded per period
    sigma, eta, gamma, tau : model parameters (see simulate_one_path)
    n_sims : int, total simulated paths (n_sims/2 antithetic pairs)
    
    Returns
    -------
    IS_raw : pd.DataFrame, all individual IS values, use for variance
    IS_paired : pd.DataFrame, antithetic pair averages, use for mean
    """
    n_periods = len(shares_traded)
    all_IS = []       # raw individual samples, for variance
    paired_IS = []     # antithetic pair averages, for mean

    for i in range(n_sims // 2):
        eps = np.random.normal(size=n_periods)
        IS_1 = simulate_one_path(S0, shares_traded, sigma, eta, gamma, tau, eps)
        IS_2 = simulate_one_path(S0, shares_traded, sigma, eta, gamma, tau, -eps)
        
        all_IS.extend([IS_1, IS_2])
        paired_IS.append((IS_1 + IS_2) / 2)

    return pd.DataFrame({'IS_raw': all_IS}), pd.DataFrame({'IS_paired': paired_IS})