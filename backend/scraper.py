import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
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
            "currency": self.socket.info["currency"],
        }

    def build_dataset(self):
        start_date = datetime(2010, 1, 1).date()
        end_date = datetime.now().date()

        try:
            self.dataset = self.socket.history(start=start_date, end=end_date, interval="1d").reset_index()
            self.dataset['Date'] = self.dataset['Date'].dt.tz_localize(None)
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
