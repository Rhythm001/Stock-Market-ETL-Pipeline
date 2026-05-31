from sqlalchemy import text
from src.logger import logger

def run_checks(engine):
    checks = [
        (
            'Null close Prices',
            'SELECT COUNT(*) FROM stock_prices_enriched WHERE close_price IS NULL'
        ),
        (
            'Zero or negative price', 
            'SELECT COUNT(*) FROM stock_prices_enriched WHERE close_price <= 0'
            ),
        (
            'Ticker count latest', 
            "SELECT COUNT(DISTINCT ticker) FROM stock_prices_enriched WHERE trade_date = (SELECT MAX(trade_date)FROM stock_prices_enriched)"),
    ]
    failures = []
    
    with engine.connect() as conn:
        for name, query in checks:
            
            logger.info(f"Running quality check: {name}")
            result = conn.execute(text(query)).scalar()
            
            if name == 'Ticker count latest':
                if result != 10:
                    failures.append(f'Failed: Only {result}/10 tickers loaded')
            else: 
                if result != 0:
                    failures.append(f'Failed: {name} ({result} violations)')
            
            # if result != 0 and name != 'Ticker count latest':
            #     failures.append(f'FAILED: {name} ({result} violations)')
            # elif name == 'Ticker count today' and result != 10:
            #     failures.append(f'FAILED: Only {result}/10 tickers loaded')
        return failures