import pandas as pd
import logging

from sqlalchemy import Engine
from etl.load.utility import upsert_on_conflict_do_nothing

# ─── Configuração ────────────────────────────────────────────────────────────


logger = logging.getLogger(__name__)

TABLE_NAME = 'market_data_yahoo'


# ─── Funções ────────────────────────────────────────────────────────────

def get_max_date(engine: Engine):
    query = f'SELECT MAX(date) as max_date FROM raw.{TABLE_NAME}' 
    df = pd.read_sql(query, engine)

    max_date = df['max_date'].item()

    return max_date




def insert_new_records(df: pd.DataFrame, engine: Engine) -> int:
    if df.empty:
        return 0
    
    df.columns = df.columns.str.lower()
    df.columns = df.columns.str.replace(' ', '_')


    try:
        df.to_sql(
            'market_data_yahoo',
            engine,
            if_exists='append',
            index=False,
            schema='raw',
            method=upsert_on_conflict_do_nothing
        )
        logger.info('to_sql executado sem exceção.')
    except Exception as e:
        logger.error(f'Erro no to_sql: {type(e).__name__}: {e}')
        raise

    return len(df)
