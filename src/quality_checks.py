from sqlalchemy import text
from src.logger import logger

def run_checks(engine):
    checks = [
        ('Null close Prices',
         'SELECT COUNT(*) FROM stock_prices_enriched WHERE close_price IS NULL'),
        ('Zero or negative price', 'SELECT COUNT(*) FROM stock_prices_enriched WHERE close_price <= 0'),
        ('Ticker count today', "SELECT COUNT(DISTINCT ticker) FROM stock_prices_enriched WHERE trade_date = CURRENT_DATE - 1"),
    ]
    failures = []
    
    with engine.connect() as conn:
        for name, query in checks:
            logger.info("Starting ETL pipeline")
            result = conn.execute(text(query)).scalar()
            if result != 0 and name != 'Ticker count today':
                failures.append(f'FAILED: {name} ({result} violations)')
            elif name == 'Ticker count today' and result != 10:
                failures.append(f'FAILED: Only {result}/10 tickers loaded')
        return failures