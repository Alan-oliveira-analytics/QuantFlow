import logging

import pandas as pd
from config.db import get_engine

from etl.extract.incremental.coingecko import extract_coingecko_data
from etl.load.load import upsert_on_conflict_do_nothing, load_data





# ─── Configuração ────────────────────────────────────────────────────────────

pd.set_option('display.max_columns', None)


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)
logger = logging.getLogger(__name__)


# ─── Funções ────────────────────────────────────────────────────────────


def run():

    logger.info('Starting Coingecko data snapshot')

    df = extract_coingecko_data()
    df['extraction_time'] = pd.Timestamp.now()

    for col in df.columns:
        if df[col].apply(lambda x: isinstance(x, dict)).any():
            df = df.drop(columns=[col])

    engine = get_engine()

    inserted = load_data(df, engine, 'market_cryptos', method=upsert_on_conflict_do_nothing)

    logger.info(f'{inserted} new records inserted.')



if __name__ == '__main__':
    run()