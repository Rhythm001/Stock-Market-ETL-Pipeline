from sqlalchemy import create_engine
import pandas as pd

def load_to_postgres(df, table_name, engine):
    df.to_sql(
        name = table_name,
        con = engine,
        if_exists = 'append',
        index = False,
        method = 'multi'  # batch insert - for performance
    )
    
