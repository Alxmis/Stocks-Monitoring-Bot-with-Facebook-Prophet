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

    def fetch_data(self, mode: str, days: int, interval: str, symbol=None) -> pd.DataFrame:
        # Get adj_close data for all stocks in list
        if mode == 'adj_close':
            try:
                data = pd.DataFrame(columns=self.symbols_list)
                for ticker in self.symbols_list:
                    end_date = datetime.today()
                    start_date = end_date - timedelta(days=days) # When calling func days=2
                    data[ticker] = yf.download(ticker,
                                               start=start_date,
                                               end=end_date,
                                               interval=interval)['Adj Close']
                return data
            except Exception as e:
                error_handler.raise_error(
                    msg=f"Failed to fetch data: {str(e)}."
                )

        # Get all data for one stock
        elif mode == 'stock_data':
            if symbol == None:
                error_handler.raise_error(
                    msg=f"Forget to mention symbol."
                )

            try:
                end_date = datetime.today()
                start_date = end_date - timedelta(days=days) # TODO: days
                ticker_data = yf.download(symbol,
                                          start=start_date,
                                          end=end_date,
                                          interval=interval) # TODO: period
                return ticker_data
            except Exception as e:
                error_handler.raise_error(
                    msg=f"Failed to fetch full data for {symbol}: {str(e)}."
                )

    def check_spike(self, data: pd.DataFrame) -> Union[bytes, bool]:
        spikes_data = data.pct_change().dropna()
        skyrockets_data = spikes_data[abs(spikes_data) > THRESHOLD].dropna(how='all', axis=1)
        return skyrockets_data if not skyrockets_data.empty else False


    # def make_plot(self, raw_data: pd.DataFrame, symbol: str) -> bytes:
    #     stock_data = raw_data[symbol]
    #
    #     plt.style.use('dark_background')
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


# scraper = Scraper()
# data = scraper.fetch_data(mode='adj_close')
# skyrockets_data = scraper.check_spike(data=data)
# print(skyrockets_data)