import os
import logging
from sqlalchemy import create_engine, text
import pandas as pd
from src.logger import logger
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

# def get_engine():
#     DB_URL = os.getenv("DB_URL")
#     return create_engine(DB_URL)

# def load_to_postgres(df, table_name):
#     engine = get_engine() # 'postgresql://postgres:rhythm123@localhost:5432/postgres'
#     with engine.begin() as conn:
#         df.to_sql(
#             name = '_temp_load',
#             con = DB_URL,
#             if_exists = 'replace',
#             index = False #,
#             # method = 'multi'  # batch insert - for performance  
#         )
            
#     # with engine.begin() as conn:
#     columns = ', '.join(df.columns)
    
#     result = conn.execute(text(f"""
#                     INSERT INTO {table_name} ({columns})
#                     SELECT {columns} FROM _temp_load
#                     ON CONFLICT (ticker, trade_date) DO NOTHING;
#                     """))
#     inserted = result.rowcount
#     skipped = len(df) - inserted
#     # conn.commit()
#     # conn.execute(text("COMMIT"))
#     logger.info(f"Inserted {inserted}, skipped {skipped} duplicates")

def load_to_postgres(df, table_name):
    DB_URL = os.getenv("DB_URL")
    engine = create_engine(DB_URL)
    
    with engine.begin() as conn:
        # Create temp table matching the dataframe structure
        conn.execute(text("DROP TABLE IF EXISTS _temp_load"))
        conn.execute(text(f"""
            CREATE TEMP TABLE _temp_load AS 
            SELECT * FROM {table_name} WHERE 1=0
        """))
        
        # Insert rows one by one using SQLAlchemy (no pandas to_sql)
        rows = df.to_dict(orient='records')
        columns = ', '.join(df.columns)
        placeholders = ', '.join([f':{col}' for col in df.columns])
        
        conn.execute(
            text(f"INSERT INTO _temp_load ({columns}) VALUES ({placeholders})"),
            rows
        )
        
        result = conn.execute(text(f"""
            INSERT INTO {table_name} ({columns})
            SELECT {columns} FROM _temp_load
            ON CONFLICT (ticker, trade_date) DO NOTHING
        """))
        inserted = result.rowcount
        skipped = len(df) - inserted
        logger.info(f"Inserted {inserted}, skipped {skipped} duplicates")