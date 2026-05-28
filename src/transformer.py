import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text 
from pathlib import Path
from logger import logger


load_dotenv()
DB_URL = os.getenv('DB_URL')
SQL_PATH = Path('sql/transform_indicators.sql')

def run_transformation():
    engine = create_engine(DB_URL)
    sql = SQL_PATH.read_text()
    
    with engine.connect() as conn:
        conn.execute(text(sql))
        conn.commit()
        
    logger.info("Transformation complete.")
    
if __name__ == '__main__':
    run_transformation()