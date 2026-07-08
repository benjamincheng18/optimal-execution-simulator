import numpy as np

def twap_schedule(X, N):
    """
    Compute the TWAP (equal-split) execution schedule.
    
    Parameters
    ----------
    X : float, total shares to execute
    N : int, number of periods
    
    Returns
    -------
    np.array of length N, shares traded per period
    """
    twap_shares_traded = np.full(N, X/N)
    return twap_shares_traded


def vwap_schedule(X, volume_series):
    """
    Compute the VWAP (volume-proportional) execution schedule.
    
    Parameters
    ----------
    X : float, total shares to execute
    volume_series : np.array or pd.Series, historical volume per period
    
    Returns
    -------
    np.array of length len(volume_series), shares traded per period, proportional to volume, summing to X
    """
    weight_per_period = volume_series / sum(volume_series)
    vwap_shares_traded = X * weight_per_period
    return vwap_shares_traded