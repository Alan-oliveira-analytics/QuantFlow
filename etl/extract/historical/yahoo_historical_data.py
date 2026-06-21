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


output_path = DATA_DIR / 'raw' / 'yfinance' / 'yfinance_data.csv'

assets = ['AAPL', 'MSFT', 'NVDA', 'AMZN', 'GOOGL', 'QQQ', 'SPY']

df = pd.DataFrame()


# ─── Funções ────────────────────────────────────────────────────────────

def extract_yfinance_data(assets, df, period='5y'):

    for asset in assets:
        logger.info(f'[{asset}] Buscando histórico ({period})...')
        ticker = yf.Ticker(asset)
        data = ticker.history(period=period)
        data['ticker'] = asset
        df = pd.concat([df, data])

    df.reset_index(inplace=True)

    return df


def main(df):

    folder_path = output_path.parent
    folder_path.mkdir(parents=True, exist_ok=True)

    if output_path.exists():
        logger.info('Arquivo existente encontrado. Combinando com os novos dados...')
        existing_df = pd.read_csv(output_path)
        existing_df['Date'] = pd.to_datetime(existing_df['Date'], utc=True)

        combined_df = pd.concat([existing_df, df], ignore_index=True)
        combined_df.drop_duplicates(subset=['Date', 'ticker'], keep='last', inplace=True)

        combined_df.to_csv(output_path, index=False)

    else:
        logger.info('Nenhum arquivo anterior encontrado. Criando novo dataset...')
        df.to_csv(output_path, index=False)

    logger.info(f'Dados salvos em {output_path}.')



if __name__ == '__main__':
    df = extract_yfinance_data(assets, df)
    main(df)
