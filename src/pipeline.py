from extractor import extract_all
from loader import load_to_postgres
from transformer import run_transformation

COLUMN_RENAME_MAP = {
    'Date' : 'trade_date',
    'Open' : 'open_price',
    'High' : 'high_price',
    'Low' : 'low_price',
    'Close' : 'close_price',
    'Volume' : 'volume'
}

COLUMNS_TO_DROP = ['Dividends', 'Stock Splits', 'Capital Gains']

FINAL_COLUMNS = ['ticker', 'trade_date', 'open_price', 'high_price', 'low_price', 'close_price', 'volume']


def clean_dataframe(df, ticker):
    # Date is in the index in the yfinance output. Bring it in the dataframe
    df = df.reset_index()
    
    # rename to match SQL schema
    df = df.rename(columns=COLUMN_RENAME_MAP)
    
    # Drop noisy columns if they exist
    df = df.drop(columns = [col for col in COLUMNS_TO_DROP if col in df.columns])
    
    # Confirm ticker column exists after the reset index
    if 'ticker' not in df.columns:
        print("uh-oh, ticker got removed")
        df['ticker']  = ticker
        
    # Strip time-zone from trade_date if present (Postsgres doesn't like tz-aware dates in DATE column)
    if df['trade_date'].dtype == 'datetime64[ns, UTC]' or hasattr(df['trade_date'], 'dt'):
        df['trade_date'] = df['trade_date'].dt.tz_localize(None)
        
    # Keep only the columns that the table expects, in the right order
    df = df[FINAL_COLUMNS]
    
    return df

def run_pipeline():
    print("Extraction started.")
    raw_data = extract_all()
    print(f"Extracted data for {len(raw_data)} tickers.")
    
    for ticker, df in raw_data.items():
        print(f"Processing {ticker}...")
        cleaned_df = clean_dataframe(df, ticker)
        load_to_postgres(cleaned_df, 'stock_prices_raw')
        print(f"Loaded {len(cleaned_df)} rows for {ticker}")
    
    print("Running transformations...")
    run_transformation()
        
    print("Pipeline complete.")
    
if __name__ == '__main__':
    run_pipeline()