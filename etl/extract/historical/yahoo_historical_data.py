import yfinance as yf
import pandas as pd
from pathlib import Path
from config.paths import DATA_DIR


output_path = DATA_DIR / 'raw' / 'yfinance_data.csv'

assets = ['AAPL', 'MSFT', 'NVDA', 'AMZN', 'GOOGL', 'QQQ', 'SPY']

df = pd.DataFrame()


def extract_yfinance_data(assets, df, period='5y'):

    for asset in assets:
        ticker = yf.Ticker(asset)
        data = ticker.history(period=period)
        data['ticker'] = asset
        df = pd.concat([df, data])

    df.reset_index(inplace=True)

    return df



df = extract_yfinance_data(assets, df)


def main():
    df.to_csv(output_path, index=False)



if __name__ == '__main__':
    main()