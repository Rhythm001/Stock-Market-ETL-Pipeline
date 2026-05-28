from extractor import extract_all
from quality_checks import run_checks
from loader import load_to_postgres
from transformer import run_transformation
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os
from logger import logger

load_dotenv()
DB_URL = os.getenv("DB_URL")
engine = create_engine(DB_URL)

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
        logger.warning(f"{ticker}: ticker column missing, restoring manually")
        df['ticker']  = ticker
        
    # Strip time-zone from trade_date if present (Postsgres doesn't like tz-aware dates in DATE column)
    if pd.api.types.is_datetime64_any_dtype(df['trade_date']):
        df['trade_date'] = df['trade_date'].dt.tz_localize(None)
        
    # Keep only the columns that the table expects, in the right order
    df = df[FINAL_COLUMNS]
    
    return df

def run_pipeline():
    try:
        logger.info("Pipeline Started.")
        
        logger.info("Extraction Started")
        raw_data = extract_all()
        logger.info(f"Extracted data for {len(raw_data)} tickers.")
        
        for ticker, df in raw_data.items():
            logger.info(f"Processing {ticker}...")
            
            cleaned_df = clean_dataframe(df, ticker)
            
            load_to_postgres(cleaned_df, 'stock_prices_raw')
            logger.info(f"Loaded {len(cleaned_df)} rows for {ticker}")
        
        logger.info("Running transformations...")
        run_transformation()
        logger.info("Indicators computed successfully")
        
        failures = run_checks(engine)
        logger.info(f"Quality checks completed. Failures: {len(failures)}")
        
        if failures:
            raise Exception("\n".join(failures))

        logger.info("Pipeline completed successfully.")
        
    except Exception as e:
        logger.exception(f"Pipeline failed: {e}")
        raise
    
if __name__ == '__main__':
    run_pipeline()