import numpy as np
import pandas as pd

def compute_kappa(lam, sigma, eta, gamma, tau):
    """
    Compute the urgency parameter kappa for the Almgren-Chriss trajectory.
    
    Parameters
    ----------
    lam : float, risk-aversion parameter
    sigma : float, volatility of the asset (per unit time, matching tau's units)
    eta : float, temporary impact parameter
    gamma : float, permanent impact parameter
    tau : float, length of one trading interval (T / N)
    
    Returns
    -------
    kappa : float
    """
    kappa_tilde_sq = (lam * sigma**2) / (eta * (1 - gamma*tau/(2*eta)))
    
    kappa = (np.arccosh((tau**2 * kappa_tilde_sq) / 2 + 1)) / tau
    
    return kappa


def almgren_chriss_trajectory(X, T, N, lam, sigma, eta, gamma):
    """
    Compute the optimal Almgren-Chriss execution trajectory.
    
    Parameters
    ----------
    X : float, total shares to execute
    T : float, total time horizon
    N : int, number of discrete trading intervals
    lam, sigma, eta, gamma : model parameters (see compute_kappa)
    
    Returns
    -------
    pd.DataFrame with columns: time, shares_remaining, shares_traded
    """
    tau = T / N
    kappa = compute_kappa(lam, sigma, eta, gamma, tau)
    
    k = np.arange(N+1)
    
    shares_remaining = X * np.sinh(kappa * (T - k*tau)) / np.sinh(kappa * T)
    
    shares_traded = -np.diff(shares_remaining)
    shares_traded = np.insert(shares_traded, 0, np.nan)
    
    df = pd.DataFrame({
        'time': k * tau,
        'shares_remaining': shares_remaining,
        'shares_traded': shares_traded
    })
    
    return df