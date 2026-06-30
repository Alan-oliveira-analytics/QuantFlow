import logging
import pandas as pd

from config.paths import BASE_DIR, DATA_DIR
from config.db import get_engine
from config.logging import setup_logging

from etl.load.utility import upsert_on_conflict_do_nothing

# ─── Configuração ────────────────────────────────────────────────────────────

pd.set_option('display.max_columns', None)


base_btc_path = DATA_DIR / 'raw' / 'bitcoin'


logger = logging.getLogger(__name__)



# ─── Funções ────────────────────────────────────────────────────────────



def load_data(df, engine, table_name, schema='raw', if_exists='append'):

    df.columns = df.columns.str.lower()
    df.columns = df.columns.str.replace(' ', '_')

    inserted = df.to_sql(
        name=table_name,
        con=engine,
        if_exists=if_exists,
        index=False,
        schema=schema,
        method=upsert_on_conflict_do_nothing
    )

    return inserted


def main():

    setup_logging()

    engine = get_engine()

    df_yfinance = pd.read_csv(BASE_DIR / 'data' / 'raw' / 'yfinance' / 'yfinance_data.csv')
    df_historical_data_btc = pd.read_csv(BASE_DIR / 'data' / 'raw' / 'bitcoin' / 'bitcoin_historical_data.csv')


    load_data(df_yfinance, engine, 'market_data_yahoo')
    load_data(df_historical_data_btc, engine, 'market_data_historical_btc')

    files = base_btc_path.rglob('*.parquet')

    for file in files:
        df = pd.read_parquet(file)

        for col in df.columns:
            if df[col].apply(lambda x: isinstance(x, dict)).any():
                df = df.drop(columns=[col])

        load_data(df, engine, 'market_cryptos')


if __name__ == '__main__':
    main()
