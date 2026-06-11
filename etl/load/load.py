from sqlalchemy import create_engine
from sqlalchemy.dialects.postgresql import insert
from urllib.parse import quote_plus
import os
from pathlib import Path
import pandas as pd
from dotenv import load_dotenv
from config.paths import BASE_DIR, DATA_DIR

pd.set_option('display.max_columns', None)


base_btc_path = DATA_DIR / 'raw' / 'bitcoin'
env_path = BASE_DIR / '.env'


load_dotenv(env_path)



user = os.getenv('POSTGRES_USER')
password = os.getenv('POSTGRES_PASSWORD')
database = os.getenv('POSTGRES_DB')

host = 'localhost'


def get_engine():

    print('Creating database engine...')

    return create_engine(
        f'postgresql+psycopg2://{user}:{quote_plus(password)}@{host}:5433/{database}'
    )


engine = get_engine()

def upsert_on_conflict_do_nothing(table, conn, keys, data_iter):
    data = [dict(zip(keys, row)) for row in data_iter]
    stmt = insert(table.table).values(data).on_conflict_do_nothing()
    conn.execute(stmt)


def load_data(df, engine, table_name, schema='raw', if_exists='append'):
    
    df.columns = df.columns.str.lower()
    df.columns = df.columns.str.replace(' ', '_')

    df.to_sql(
        name=table_name,
        con=engine,
        if_exists=if_exists,
        index=True,
        schema=schema,
        method=upsert_on_conflict_do_nothing
    )

    print('Data loading completed successfully.')

    df_check = pd.read_sql(f'SELECT * FROM raw.{table_name}', con=engine)

    print(f'Number of records in {table_name}: {len(df_check)}')


df_yfinance = pd.read_csv(BASE_DIR / 'data' / 'raw' / 'yfinance' / 'yfinance_data.csv')
df_historical_data_btc = pd.read_csv(BASE_DIR / 'data' / 'raw' / 'bitcoin' / 'bitcoin_historical_data.csv')
df_historical_data_fred = pd.read_parquet(BASE_DIR / 'data' / 'raw' / 'fred' / 'fred_data.parquet', engine='pyarrow')


def main():
    load_data(df_yfinance, engine, 'market_data_yahoo')
    load_data(df_historical_data_btc, engine, 'market_data_historical_btc')
    load_data(df_historical_data_fred, engine, 'market_data_historical_fred')

    files = base_btc_path.rglob('*.parquet')

    for file in files:
        df = pd.read_parquet(file)

        for col in df.columns:
            if df[col].apply(lambda x: isinstance(x, dict)).any():
                df = df.drop(columns=[col])

        load_data(df, engine, 'market_cryptos')


if __name__ == '__main__':
    main()