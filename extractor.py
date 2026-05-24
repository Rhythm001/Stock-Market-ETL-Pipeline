import yfinance as yf
import time

TICKERS = ['INFY.NS', 'TCS.NS', 'WIPRO.NS', 'HCLTECH.NS', 'TECHM.NS', 'AAPL', 'MSFT', 'GOOGL', 'META', 'AMZN']
# .NS suffix on Indian tickers fetches data from NSE. Without it, yfinance defaults to US markets.


def fetch_ticker(ticker, retries = 3):
    for attempt in range(retries):
        try:
            df = yf.ticker(ticker).history(period='60d')
            if df.empty:
                return None   # Market holiday or no data
            df['ticker'] = ticker
            return df
        except Exception as e:
            wait = 5* (2**attempt) # exponential backoff: 5s, 10s, 20s
            time.sleep(wait)
    return None  # all retries exhausted


def extract_all():
    results = {}
    for ticker in TICKERS:
        df = fetch_ticker(ticker)
        if df is not None:
            results[ticker] = df
    return results

