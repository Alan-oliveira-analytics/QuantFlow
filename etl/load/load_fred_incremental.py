from urllib.parse import quote_plus
from etl.load.load import load_data, engine

import requests
import pandas as pd
from dotenv import load_dotenv
import pyarrow
import os
import logging
from datetime import datetime

from sqlalchemy import Engine, text

from config.paths import BASE_DIR



# ─── Configuração ────────────────────────────────────────────────────────────
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)

logger = logging.getLogger(__name__)

TABLE_NAME = 'market_data_historical_fred'


def get_max_date_by_series(engine: Engine) -> dict:
    query = f'SELECT series, MAX(date) as max_date FROM raw.{TABLE_NAME} GROUP BY series' 
    df = pd.read_sql(query, engine)

    return dict(zip(df['series'], df['max_date']))



def insert_new_records(df: pd.DataFrame, engine: Engine) -> int:
    if df.empty:
        return 0
    
    # ─── Diagnóstico 1: valida conexão e search_path ──────────────────
    with engine.connect() as conn:
        search_path = conn.execute(text("SHOW search_path")).scalar()
        current_user = conn.execute(text("SELECT current_user")).scalar()
        
        schema_exists = conn.execute(text("""
            SELECT schema_name 
            FROM information_schema.schemata 
            WHERE schema_name = 'raw'
        """)).scalar()
        
        table_exists = conn.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'raw' 
            AND table_name = 'market_data_historical_fred'
        """)).scalar()

        logger.info(f'search_path ativo:   {search_path}')
        logger.info(f'usuário conectado:   {current_user}')
        logger.info(f'schema raw existe:   {schema_exists}')
        logger.info(f'tabela existe em raw: {table_exists}')

    # ─── Diagnóstico 2: valida colunas do DataFrame vs tabela ─────────
    logger.info(f'Colunas do DataFrame: {df.dtypes.to_dict()}')


    # ─── Diagnóstico 3: tenta inserir e captura erro explícito ────────
    try:
        df.to_sql(
            'market_data_historical_fred',
            engine,
            if_exists='append',
            index=True,
            schema='raw',
        )
        logger.info('to_sql executado sem exceção.')
    except Exception as e:
        logger.error(f'Erro no to_sql: {type(e).__name__}: {e}')
        raise

    return len(df)



