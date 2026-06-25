import requests
import pandas as pd
from dotenv import load_dotenv
import os
import logging
from datetime import datetime
from config.paths import BASE_DIR


# ─── Configuração ────────────────────────────────────────────────────────────

env_path = BASE_DIR / '.env'

load_dotenv(env_path)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)
logger = logging.getLogger(__name__)

api_key = os.getenv('API_KEY')

url = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids=bitcoin&names=Bitcoin&symbols=btc&category=layer-1&price_change_percentage=1h"

headers = {"x-cg-demo-api-key": api_key}


year = datetime.now().year
month = datetime.now().strftime('%m')
day = datetime.now().strftime('%d')


# ─── Funções ────────────────────────────────────────────────────────────


def extract_coingecko_data(url=url, headers=headers) -> pd.DataFrame:
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame(data)

    else:
        logger.error(f'Error: {response.status_code} - {response.text}')
        return pd.DataFrame()
 
    return df


def main():
    df = extract_coingecko_data(url, headers)

    if df.empty:
        logger.warning('No data extracted.')
        return

    df['extraction_time'] = pd.Timestamp.now()

    folder_path = BASE_DIR / 'data' / 'raw' / 'bitcoin' / f'year={year}' / f'month={month}'

    folder_path.mkdir(parents=True, exist_ok=True)


    file_path = folder_path / f'{year}-{month}-{day}.parquet'


    if file_path.exists():
        existing_df = pd.read_parquet(file_path, engine='pyarrow')

        final_df = pd.concat([existing_df, df], ignore_index=True)

        final_df = final_df.drop_duplicates(subset=['last_updated'])

    else:
        final_df = df

    final_df.to_parquet(file_path, index=False, engine='pyarrow')

    logger.info(f'Data extracted and saved to {file_path}')


if __name__ == '__main__':
    main()
