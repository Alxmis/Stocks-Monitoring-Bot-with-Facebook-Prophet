import matplotlib.pyplot as plt, matplotlib.dates as mdates
import pandas as pd
import numpy as np
import pandas_ta as ta
from datetime import datetime, timedelta
from io import BytesIO

class Analyzer:
    def __init__(self, ticker: str, data: pd.DataFrame) -> None:
        self.ticker = ticker
        self.data = data

    def analyze(self) -> None:
        one_year_ago = datetime.now() - timedelta(days=365)
        adv_data = self.data[self.data['Date'] >= one_year_ago].copy()

        adv_data.ta.macd(append=True)
        adv_data.ta.rsi(append=True)
        adv_data.ta.bbands(append=True)
        adv_data.ta.obv(append=True)

        adv_data.ta.sma(length=20, append=True)
        adv_data.ta.ema(length=50, append=True)
        adv_data.ta.stoch(append=True)
        adv_data.ta.adx(append=True)

        adv_data.ta.willr(append=True)
        adv_data.ta.cmf(append=True)
        adv_data.ta.psar(append=True)

        adv_data['OBV_in_million'] = adv_data['OBV']/1e7

        adv_data.iloc[:, 1:] = adv_data.iloc[:, 1:].round(2)

        self.adv_data = adv_data

    def get_description(self):
        start_date = self.adv_data.index[0]
        end_date = self.adv_data.index[1]

        start_price = self.adv_data.loc[start_date, 'Close']
        end_price = self.adv_data.loc[end_date, 'Close']
        price_change = (end_price - start_price) / start_price

        start_volume = self.adv_data.loc[start_date, 'Volume']
        end_volume = self.adv_data.loc[end_date, 'Volume']
        volume_change = (end_volume - start_volume) / start_volume

        price_directions = {1: "increased", -1: "decreased", 0: None}
        volume_directions = {1: "increased", -1: "decreased", 0: None}

        price_change_direction = price_directions[np.sign(price_change)]
        volume_change_direction = volume_directions[np.sign(volume_change)]

        description = (f"📈 A price spike has been detected for {self.ticker}. Date: {self.adv_data.reset_index().iloc[1, 1].strftime('%Y-%m-%d')}.\n\n"
                       f"💰 Closing price: {end_price}\n")

        if price_change_direction:
            description += f"📊 Price {price_change_direction} by {abs(price_change * 100):.2f}%.\n"
        if volume_change_direction:
            description += f"📉 Volume {volume_change_direction} by {abs(volume_change * 100):.2f}%.\n"

        return description


    @staticmethod
    def save_plot_to_bytes() -> bytes:
        buf = BytesIO()
        plt.savefig(buf, format='png', dpi=300)
        buf.seek(0)
        return buf.getvalue()

    def make_tech_plots(self) -> dict:
        plot_images = {}

        columns = self.adv_data.columns

        # Price Trend Chart for 1 year
        plt.figure()
        plt.plot(self.adv_data.set_index('Date').index, self.adv_data['Close'], label='Close', color='blue')
        plt.title(f"Price Trend of {self.ticker}")
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
        plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
        plt.xticks(rotation=45, fontsize=8)
        plot_images['PT'] = self.save_plot_to_bytes()

        # On-Balance Volume Chart
        if 'OBV' in columns:
            plt.figure()
            plt.plot(self.adv_data['OBV'], label='On-Balance Volume')
            plt.title(f"On-Balance Volume (OBV) Indicator of {self.ticker}")
            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y %b'))
            plt.gca().xaxis.set_major_locator(mdates.YearLocator())
            plt.xticks(rotation=45, fontsize=8)
            plot_images['OBV'] = self.save_plot_to_bytes()

        plt.close()
        return plot_images