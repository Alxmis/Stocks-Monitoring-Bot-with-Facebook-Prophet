import numpy as np
from prophet import Prophet
import matplotlib.pyplot as plt
import yfinance as yf
import pandas as pd
from io import BytesIO

# TODO: move to another file
import warnings
warnings.filterwarnings('ignore')

class Predictor():
    def __init__(self, stock_price: pd.DataFrame) -> None:
        self.stock_price = stock_price
        self.model = None

    def train_model(self) -> None:
        self.stock_price = self.stock_price.reset_index().rename(columns={'Date': 'ds', 'Adj Close': 'y'})

        self.model = Prophet()
        self.model.add_country_holidays(country_name='US')

        self.model.fit(self.stock_price)

    def make_forecast(self, periods=365) -> pd.DataFrame: # TODO: periods
        future = self.model.make_future_dataframe(periods=periods, freq='d')
        future_boolean = future['ds'].map(lambda x: True if x.weekday() in range(0, 5) else False)
        future = future[future_boolean]

        stock_price_forecast = self.model.predict(future)
        return stock_price_forecast

    @staticmethod
    def save_plot_to_bytes() -> bytes:
        buf = BytesIO()
        plt.savefig(buf, format='png', dpi=300)
        buf.seek(0)
        return buf.getvalue()

    def make_forecast_plot(self, stock_price_forecast):
        plot_images = {}
        forecast_plot = self.model.plot(stock_price_forecast)
        plot_images['forecast_plot'] = self.save_plot_to_bytes()
        forecast_components_plot = self.model.plot_components(stock_price_forecast)
        plot_images['forecast_components_plot'] = self.save_plot_to_bytes()

        plt.close()

