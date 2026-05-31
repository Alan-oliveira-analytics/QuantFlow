import requests
from pathlib import Path
import pandas as pd
from dotenv import load_dotenv
import os

BASE_DIR = Path(__file__).resolve().parent.parent.parent

env_path = BASE_DIR / '.env'

load_dotenv(env_path)

api_key = os.getenv('API_KEY')

url = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids=bitcoin&names=Bitcoin&symbols=btc&category=layer-1&price_change_percentage=1h"

headers = {"x-cg-demo-api-key": api_key}


def extract_coingecko_data(url, headers) -> pd.DataFrame:
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame(data)

    else:
        print(f'Error: {response.status_code} - {response.text}')
        return pd.DataFrame()

    return df


def main():
    df = extract_coingecko_data(url, headers)
    output_path = BASE_DIR / 'data' / 'raw' / 'coingecko_data.csv'
    df.to_csv(output_path, index=False)


if __name__ == '__main__':
    main()