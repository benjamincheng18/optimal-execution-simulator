import yfinance as yf
import pandas as pd
import numpy as np

def fetch_raw_data(ticker, interval, start, end):
    """
    Fetch intraday OHLCV data from yfinance.
    
    Parameters
    ----------
    ticker : str
    interval : str, e.g. '5m'
    start, end : str, date range (yfinance format)
    
    Returns
    -------
    pd.DataFrame with OHLCV columns, datetime index
    """
    data = yf.download(ticker, start, end, interval)[["Close", "Volume"]]
    data.columns = data.columns.get_level_values(0)
    return data


def avg_volume(raw_data):
    """
    Compute average volume per time-of-day bucket, across all days in raw_data.
    
    Parameters
    ----------
    raw_data : pd.DataFrame, output of fetch_raw_data, datetime index
    
    Returns
    -------
    pd.DataFrame, single column 'volume', indexed by time-of-day
    """
    time_of_day = raw_data.index.time
    avg_vol = raw_data.groupby(time_of_day)["Volume"].mean()
    return avg_vol.to_frame(name='volume')


def volatility(raw_data, tau, interval):
    """
    Compute realized volatility from price returns, scaled to match tau's time unit.
    
    Parameters
    ----------
    raw_data : pd.DataFrame, output of fetch_raw_data
    tau : float, target time unit (e.g. fraction of a trading day) that sigma should match
    
    Returns
    -------
    float, volatility (sigma) scaled to tau
    """
    returns = raw_data["Close"].pct_change()
    std_returns = np.std(returns)
    sigma = std_returns * np.sqrt(tau*6.5*60 / int(interval.replace('m','')))
    return sigma