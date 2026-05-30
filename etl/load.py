from sqlalchemy import create_engine
from urllib.parse import quote_plus
import os
from pathlib import Path
import pandas as pd
from dotenv import load_dotenv



BASE_DIR = Path(__file__).resolve().parent.parent

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


def load_data(table_name, df):
    df.to_sql(
        name=table_name,
        con=engine,
        if_exists='replace',
        index=False,
        schema='raw'
        
    )

    print('Data loading completed successfully.')

    df_check = pd.read_sql(f'SELECT * FROM {table_name}', con=engine)

    print(f'Number of records in {table_name}: {len(df_check)}')


df = pd.read_csv(BASE_DIR / 'data' / 'raw' / 'yfinance_data.csv')

load_data('market_data', df)