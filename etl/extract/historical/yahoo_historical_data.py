import yfinance as yf
import pandas as pd
from pathlib import Path
from config.paths import DATA_DIR


output_path = DATA_DIR / 'raw' / 'yfinance' / 'yfinance_data.csv'

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

    folder_path = output_path.parent
    folder_path.mkdir(parents=True, exist_ok=True)

    if output_path.exists():
        existing_df = pd.read_csv(output_path)
        existing_df['Date'] = pd.to_datetime(existing_df['Date'], utc=True)

        combined_df = pd.concat([existing_df, df], ignore_index=True)
        combined_df.drop_duplicates(subset=['Date', 'ticker'], keep='last', inplace=True)

        combined_df.to_csv(output_path, index=False)

    else:
        df.to_csv(output_path, index=False)



if __name__ == '__main__':
    main()