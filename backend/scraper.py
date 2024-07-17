import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from io import BytesIO
from libs import error_handler
from typing import Union

THRESHOLD = 0.004 # TODO

class Dataset:
    def __init__(self, ticker):
        self.ticker = ticker
        self.socket = yf.Ticker(self.ticker)
        self.info = {
            "sector": self.socket.info["sector"],
            "summary": self.socket.info["longBusinessSummary"],
            "country": self.socket.info["country"],
            "website": self.socket.info["website"],
            "employees": self.socket.info["fullTimeEmployees"],
        }

    def build_dataset(self):
        start_date = datetime(2010, 1, 1).date()
        end_date = datetime.now().date()

        try:
            self.dataset = self.socket.history(start=start_date, end=end_date, interval="1d").reset_index()
            self.dataset['Date'] = self.dataset['Date'].dt.tz_localize(None)

            # self.dataset.drop(columns=["Dividends", "Stock Splits", "Volume"], inplace=True)
            # self.add_forecast_date()
        except Exception as e:
            print("Exception raised at: 'predictor.Dataset.build()", e)
            return False
        else:
            return self.dataset

    def check_spike(self) -> Union[bytes, bool]:
        day_number = datetime.now().date().isoweekday()
        if day_number in [6, 7]:
            raise Exception("Today is weekend! Stock exchange doesn't work!")

        start_date = datetime.now().date() - timedelta(days=2)
        end_date = datetime.now().date()
        spike_level = self.socket.history(start=start_date, end=end_date, interval="1d")['Close'].pct_change().dropna().iloc[0]
        if abs(spike_level) > THRESHOLD:
            print(f"Spike detected. Ticker: {self.ticker}")
            return abs(spike_level)
        else:
            return False
        # spikes_data = data.pct_change().dropna()
        # skyrockets_data = spikes_data[abs(spikes_data) > THRESHOLD].dropna(how='all', axis=1)
        # return skyrockets_data if not skyrockets_data.empty else False


    # def add_forecast_date(self):
    #     present_date = self.dataset.Date.max()
    #     day_number = pd.to_datetime(present_date).isoweekday()
    #     if day_number in [5, 6]:
    #         self.forecast_date = present_date + timedelta(days=(7 - day_number) + 1)
    #     else:
    #         self.forecast_date = present_date  + timedelta(days=1)
    #     print("Valid forcast date: ", self.forecast_date)
    #     test_row = pd.DataFrame([[self.forecast_date, 0.0, 0.0, 0.0, 0.0]], columns=self.dataset.columns)
    #     self.dataset = pd.concat([self.dataset, test_row])

# class Spikes(Dataset):
#     def check_spike(self, data: pd.DataFrame) -> Union[bytes, bool]:
#         spikes_data = data.pct_change().dropna()
#         skyrockets_data = spikes_data[abs(spikes_data) > THRESHOLD].dropna(how='all', axis=1)
#         return skyrockets_data if not skyrockets_data.empty else False
#
#

# class Scraper():
#     def __init__(self, symbols_list) -> None:
#         self.symbols_list = symbols_list
#
#
#     def fetch_data(self, mode: str, days: int, interval: str, symbol=None) -> pd.DataFrame:
#         # Get adj_close data for all stocks in list
#         if mode == 'adj_close':
#             try:
#                 data = pd.DataFrame(columns=self.symbols_list)
#                 for ticker in self.symbols_list:
#                     end_date = datetime.today()
#                     start_date = end_date - timedelta(days=days) # When calling func days=2
#                     data[ticker] = yf.download(ticker,
#                                                start=start_date,
#                                                end=end_date,
#                                                interval=interval)['Adj Close']
#                 return data
#             except Exception as e:
#                 error_handler.raise_error(
#                     msg=f"Failed to fetch data: {str(e)}."
#                 )
#
#         # Get all data for one stock
#         elif mode == 'stock_data':
#             if symbol == None:
#                 error_handler.raise_error(
#                     msg=f"Forget to mention symbol."
#                 )
#
#             try:
#                 end_date = datetime.today()
#                 start_date = end_date - timedelta(days=days) # TODO: days
#                 ticker_data = yf.download(symbol,
#                                           start=start_date,
#                                           end=end_date,
#                                           interval=interval) # TODO: period
#                 return ticker_data
#             except Exception as e:
#                 error_handler.raise_error(
#                     msg=f"Failed to fetch full data for {symbol}: {str(e)}."
#                 )
#
#     def check_spike(self, data: pd.DataFrame) -> Union[bytes, bool]:
#         spikes_data = data.pct_change().dropna()
#         skyrockets_data = spikes_data[abs(spikes_data) > THRESHOLD].dropna(how='all', axis=1)
#         return skyrockets_data if not skyrockets_data.empty else False
#
#
#     # def make_plot(self, raw_data: pd.DataFrame, symbol: str) -> bytes:
#     #     stock_data = raw_data[symbol]
#     #
#     #     plt.style.use('dark_background')
#     #     stock_data.plot(figsize=(10, 7), color='orange')
#     #     plt.title(f"Adjusted Close Price of {symbol}", fontsize=16)
#     #     plt.ylabel('Price', fontsize=14)
#     #     plt.xlabel('Time', fontsize=14)
#     #     plt.grid(which="major", color='white', linestyle='-.', linewidth=0.5)
#     #
#     #     buf = BytesIO()
#     #     plt.savefig(buf, format='png', dpi=300)
#     #     buf.seek(0)
#     #
#     #     plt.close()
#     #
#     #     return buf.getvalue()


# scraper = Scraper()
# data = scraper.fetch_data(mode='adj_close')
# skyrockets_data = scraper.check_spike(data=data)
# print(skyrockets_data)