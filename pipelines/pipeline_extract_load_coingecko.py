import logging

import pandas as pd
from config.db import get_engine
from config.logging import setup_logging

from etl.extract.incremental.coingecko import extract_coingecko_data
from etl.load.load import load_data





# ─── Configuração ────────────────────────────────────────────────────────────

pd.set_option('display.max_columns', None)


logger = logging.getLogger(__name__)


# ─── Funções ────────────────────────────────────────────────────────────


def run():

    setup_logging()

    logger.info('Starting Coingecko data snapshot')

    df = extract_coingecko_data()
    df['extraction_time'] = pd.Timestamp.now()

    for col in df.columns:
        if df[col].apply(lambda x: isinstance(x, dict)).any():
            df = df.drop(columns=[col])

    engine = get_engine()

    inserted = load_data(df, engine, 'market_cryptos')

    logger.info(f'{inserted} new records inserted.')



if __name__ == '__main__':
    run()