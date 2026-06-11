import requests
import pandas as pd
from dotenv import load_dotenv
import pyarrow
import os
from config.paths import BASE_DIR

load_dotenv()

API_KEY = os.getenv('API_KEY_FRED')

BASE_URL = 'https://api.stlouisfed.org/fred/'

ENDPOINT = 'series/observations'

file_path = BASE_DIR / 'data' / 'raw' / 'fred' / 'fred_data.parquet'

series_id = ['FEDFUNDS', 'CPIAUCSL', 'UNRATE', 'GDPC1', 'M2SL', 'DGS10']

df = pd.DataFrame()

for id in series_id:

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


folder_path = file_path.parent
folder_path.mkdir(parents=True, exist_ok=True)

df.to_parquet(file_path, index=False, engine='pyarrow')
