import pandas as pd
import logging

from sqlalchemy import Engine
from etl.load.utility import upsert_on_conflict_do_nothing



# ─── Configuração ────────────────────────────────────────────────────────────

logger = logging.getLogger(__name__)

TABLE_NAME = 'market_data_historical_fred'


# ─── Funções ────────────────────────────────────────────────────────────

def get_max_date_by_series(engine: Engine) -> dict:
    query = f'SELECT series, MAX(date) as max_date FROM raw.{TABLE_NAME} GROUP BY series' 
    df = pd.read_sql(query, engine)

    return dict(zip(df['series'], df['max_date']))



def insert_new_records(df: pd.DataFrame, engine: Engine) -> int:
    if df.empty:
        return 0
    
    
    try:
        df.to_sql(
            'market_data_historical_fred',
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



