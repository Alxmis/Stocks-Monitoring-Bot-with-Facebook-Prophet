import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from io import BytesIO
from libs import error_handler

THRESHOLD = 0.004

class Scraper():
    def __init__(self, tickers_list) -> None:
        self.tickers_list = tickers_list

    def fetch_data(self) -> pd.DataFrame:
        try:
            data = pd.DataFrame(columns=self.tickers_list)
            for ticker in self.tickers_list:
                data[ticker] = yf.download(ticker,
                                           period='2d',
                                           interval='5m')['Adj Close']
            return data
        except Exception as e:
            error_handler.raise_error(
                msg=f"Failed to fetch data: {str(e)}."
            )

    def check_spike(data: pd.DataFrame):
        spikes_data = data.pct_change().dropna()
        print(spikes_data)
        skyrockets_data = spikes_data[abs(spikes_data) > THRESHOLD].dropna(how='all', axis=1)
        return skyrockets_data if not skyrockets_data.empty else False

    def make_plot(raw_data: pd.DataFrame, ticker: str) -> bytes:
        ticker_data = raw_data[ticker]

        plt.style.use('dark_background') # TODO
        ticker_data.plot(figsize=(10, 7), color='orange')
        plt.title(f"Adjusted Close Price of {ticker}", fontsize=16)
        plt.ylabel('Price', fontsize=14)
        plt.xlabel('Time', fontsize=14)
        plt.grid(which="major", color='white', linestyle='-.', linewidth=0.5)

        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=300)
        buffer.seek(0)

        plt.close()

        return buffer.getvalue()






# make_plot(raw_data, ticker='MMM')