import yfinance as yf
import pandas as pd
import logging
from pathlib import Path
from config.paths import DATA_DIR


# ─── Configuração ────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)
logger = logging.getLogger(__name__)


file_path = DATA_DIR / 'raw' / 'yfinance' / 'yfinance_data.csv'

assets = ['AAPL', 'MSFT', 'NVDA', 'AMZN', 'GOOGL', 'QQQ', 'SPY']


df = pd.read_csv(file_path)

df['Date'] = pd.to_datetime(df['Date'], utc=True)

max_date = df['Date'].max()
next_date = max_date + pd.Timedelta(days=1)

logger.info(f'Última data no dataset: {max_date}. Buscando a partir de {next_date}...')


# ─── Funções ────────────────────────────────────────────────────────────

def extract_yfinance_data(assets, df):

    new_df = []

    for asset in assets:
        logger.info(f'[{asset}] Buscando novos dados...')
        ticker = yf.Ticker(asset)
        data = ticker.history(start=next_date)
        data['ticker'] = asset
        data.reset_index(inplace=True)
        new_df.append(data)

    if new_df:
        new_data = pd.concat(new_df, ignore_index=True)
        df = pd.concat([df, new_data], ignore_index=True)

        df.drop_duplicates(
            subset=['Date', 'ticker'],
            keep='last',
            inplace=True
        )

    return df




def main(df):
    df.to_csv(file_path, index=False)
    logger.info(f'Dados incrementais salvos em {file_path}.')



if __name__ == '__main__':
    df = extract_yfinance_data(assets, df)
    main(df)
