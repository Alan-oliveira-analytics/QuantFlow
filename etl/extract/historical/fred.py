import requests
import pandas as pd
from dotenv import load_dotenv
import os
import logging

from config.logging import setup_logging
from config.paths import BASE_DIR, ENV_PATH


# ─── Configuração ────────────────────────────────────────────────────────────

logger = logging.getLogger(__name__)


BASE_URL = 'https://api.stlouisfed.org/fred/'

ENDPOINT = 'series/observations'

file_path = BASE_DIR / 'data' / 'raw' / 'fred' / 'fred_data.parquet'

series_id = ['FEDFUNDS', 'CPIAUCSL', 'UNRATE', 'GDPC1', 'M2SL', 'DGS10']


# ─── Extração ────────────────────────────────────────────────────────────


def extract_historical_data():

    load_dotenv(ENV_PATH)

    API_KEY = os.getenv('API_KEY_FRED')


    logger.info('Iniciando a extração histórica do FRED...')

    df = pd.DataFrame()

    for id in series_id:

        logger.info(f'[{id}] Buscando observações...')

        params = {
            'api_key': f'{API_KEY}',
            'file_type': 'json',
            'series_id': id}

        response = requests.get(
            f'{BASE_URL}{ENDPOINT}',
            params=params
        )

        observations = response.json()['observations']

        series_df = pd.DataFrame(observations)
        series_df['series'] = id

        df = pd.concat([df, series_df], ignore_index=True)

        logger.info(f'[{id}] {len(series_df)} observações coletadas.')

    return df


# ─── Persistência ────────────────────────────────────────────────────────────

def main(df):

    setup_logging()

    folder_path = file_path.parent
    folder_path.mkdir(parents=True, exist_ok=True)

    df.to_parquet(file_path, index=False, engine='pyarrow')

    logger.info(f'Dados salvos em {file_path} ({len(df)} registros).')


if __name__ == '__main__':
    df = extract_historical_data()
    main(df)