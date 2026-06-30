import yfinance as yf
import pandas as pd
import logging


# ─── Configuração ────────────────────────────────────────────────────────────


logger = logging.getLogger(__name__)


# ─── Funções ────────────────────────────────────────────────────────────

def extract_yfinance_data(next_date):

    assets = ['AAPL', 'MSFT', 'NVDA', 'AMZN', 'GOOGL', 'QQQ', 'SPY']

    frames = []

    for asset in assets:
        logger.info(f'[{asset}] Buscando novos dados...')
        ticker = yf.Ticker(asset)
        data = ticker.history(start=next_date)
        data['ticker'] = asset
        data.reset_index(inplace=True)
        frames.append(data)

    return pd.concat(frames, ignore_index=True)


