import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from io import BytesIO
from libs import error_handler
from typing import Union

THRESHOLD = 0.004 # TODO

class Scraper():
    def __init__(self, symbols_list) -> None:
        self.symbols_list = symbols_list

    def fetch_data(self, mode='adj_close') -> pd.DataFrame:
        # Get adj_close data for all stocks
        if mode == 'adj_close':
            try:
                data = pd.DataFrame(columns=self.symbols_list)
                for ticker in self.symbols_list:
                    end_date = datetime.today()
                    start_date = end_date - timedelta(days=2)
                    data[ticker] = yf.download(ticker,
                                               start=start_date,
                                               end=end_date)['Adj Close']
                return data
            except Exception as e:
                error_handler.raise_error(
                    msg=f"Failed to fetch data: {str(e)}."
                )

        # Get full data for one stock
        elif mode == 'stock_data':
            try:
                symbol = self.symbols_list[0]
                end_date = datetime.today()
                start_date = end_date - timedelta(days=120) # TODO: days
                ticker_data = yf.download(symbol, start=start_date, end=end_date) # TODO: period
                return ticker_data
            except Exception as e:
                error_handler.raise_error(
                    msg=f"Failed to fetch full data for {symbol}: {str(e)}."
                )

    def check_spike(self, data: pd.DataFrame) -> Union[bytes, bool]:
        spikes_data = data.pct_change().dropna()
        print(spikes_data)
        skyrockets_data = spikes_data[abs(spikes_data) > THRESHOLD].dropna(how='all', axis=1)
        return skyrockets_data if not skyrockets_data.empty else False

    # def make_plot(self, raw_data: pd.DataFrame, symbol: str) -> bytes:
    #     stock_data = raw_data[symbol]
    #
    #     plt.style.use('dark_background') # TODO
    #     stock_data.plot(figsize=(10, 7), color='orange')
    #     plt.title(f"Adjusted Close Price of {symbol}", fontsize=16)
    #     plt.ylabel('Price', fontsize=14)
    #     plt.xlabel('Time', fontsize=14)
    #     plt.grid(which="major", color='white', linestyle='-.', linewidth=0.5)
    #
    #     buf = BytesIO()
    #     plt.savefig(buf, format='png', dpi=300)
    #     buf.seek(0)
    #
    #     plt.close()
    #
    #     return buf.getvalue()
