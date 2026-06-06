import requests
from pathlib import Path
import pandas as pd
from dotenv import load_dotenv
import os
from datetime import datetime
import pyarrow
from config.paths import BASE_DIR


env_path = BASE_DIR / '.env'

load_dotenv(env_path)

api_key = os.getenv('API_KEY')

url = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids=bitcoin&names=Bitcoin&symbols=btc&category=layer-1&price_change_percentage=1h"

headers = {"x-cg-demo-api-key": api_key}


# create a variable to store the current year, month, and day

year = datetime.now().year
month = datetime.now().month
day = datetime.now().day


# Function to extract data from CoinGecko API and return a DataFrame

def extract_coingecko_data(url, headers) -> pd.DataFrame:
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame(data)

    else:
        print(f'Error: {response.status_code} - {response.text}')
        return pd.DataFrame()

    return df


# Main function to orchestrate the extraction and saving of data to Parquet Files
def main():
    df = extract_coingecko_data(url, headers)

    if df.empty:
        print('No data extracted.')
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

    print(f'Data extracted and saved to {file_path}')


if __name__ == '__main__':
    main()

