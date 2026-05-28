import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
import pandas as pd
from logger import logger

load_dotenv()
DB_URL = os.getenv('DB_URL')
def load_to_postgres(df, table_name):
    engine = create_engine(DB_URL) # 'postgresql://postgres:rhythm123@localhost:5432/postgres'
    df.to_sql(
        name = '_temp_load',
        con = engine,
        if_exists = 'replace',
        index = False,
        method = 'multi'  # batch insert - for performance  
    )
    columns = ', '.join(df.columns)
    
    with engine.connect() as conn:
        result = conn.execute(text(f"""
                          INSERT INTO {table_name} ({columns})
                          SELECT {columns} FROM _temp_load
                          ON CONFLICT (ticker, trade_date) DO NOTHING;
                          """))
        inserted = result.rowcount
        skipped = len(df) - inserted
        conn.commit()
        logger.info(f"Inserted {inserted}, skipped {skipped} duplicates")
    
