import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import yfinance as yf
import pandas_ta as ta
from datetime import datetime, timedelta
from scraper import Scraper
from io import BytesIO

class Analyser():
    def __init__(self, stock_data: pd.DataFrame) -> None:
        self.stock_data = stock_data

    # @staticmethod # TODO: remove?
    def analyze(self) -> pd.DataFrame:
        adv_stock_data = self.stock_data
        adv_stock_data.ta.macd(append=True)
        adv_stock_data.ta.rsi(append=True)
        adv_stock_data.ta.bbands(append=True)
        adv_stock_data.ta.obv(append=True)

        adv_stock_data.ta.sma(length=20, append=True)
        adv_stock_data.ta.ema(length=50, append=True)
        adv_stock_data.ta.stoch(append=True)
        adv_stock_data.ta.adx(append=True)

        adv_stock_data.ta.willr(append=True)
        adv_stock_data.ta.cmf(append=True)
        adv_stock_data.ta.psar(append=True)

        adv_stock_data['OBV_in_million'] = adv_stock_data['OBV']/1e7
        adv_stock_data['MACD_histogram_12_26_9'] = adv_stock_data['MACDh_12_26_9'] # TODO: remove?

        last_day_summary = adv_stock_data.iloc[-1][['Adj Close',
                                                'MACD_12_26_9', 'MACD_histogram_12_26_9', 'RSI_14', 'BBL_5_2.0',
                                                'BBM_5_2.0', 'BBU_5_2.0', 'SMA_20', 'EMA_50', 'OBV_in_million',
                                                'STOCHk_14_3_3', 'STOCHd_14_3_3', 'ADX_14', 'WILLR_14', 'CMF_20',
                                                'PSARl_0.02_0.2', 'PSARs_0.02_0.2',
        ]]

        print('Summary of the last day:')
        print(last_day_summary)

        return adv_stock_data

    @staticmethod
    def save_plot_to_bytes() -> bytes:
        buf = BytesIO()
        plt.savefig(buf, format='png', dpi=300)
        buf.seek(0)
        return buf.getvalue()

    # TODO
    def draw_price_curve(self, data: pd.DataFrame, ax: plt.Axes) -> plt.Axes:
        data.plot(ax=ax, color='orange')
        # plt.title(f"Adjusted Close Price of {symbol}", fontsize=16)
        plt.ylabel('Price', fontsize=14)
        plt.xlabel('Time', fontsize=14)
        plt.grid(which="major", color='white', linestyle='-.', linewidth=0.5)

        return ax

    def make_tech_plots(self, adv_stock_data: pd.DataFrame) -> dict:
        plot_images = {}

        plt.figure(figsize=(14, 8))

        # Price Trend Chart
        plt.plot(adv_stock_data.index, adv_stock_data['Adj Close'], label='Adj Close', color='blue')
        plt.plot(adv_stock_data.index, adv_stock_data['EMA_50'], label='EMA 50', color='green')
        plt.plot(adv_stock_data.index, adv_stock_data['SMA_20'], label='SMA 20', color='orange')
        plt.title("Price Trend")
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b%d'))
        plt.xticks(rotation=45, fontsize=8)
        plt.legend()
        plot_images['PT'] = self.save_plot_to_bytes()

        # On-Balance Volume Chart
        plt.subplot(3, 3, 2)
        plt.plot(adv_stock_data['OBV'], label='On-Balance Volume')
        plt.title('On-Balance Volume (OBV) Indicator')
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b%d'))
        plt.xticks(rotation=45, fontsize=8)
        plt.legend()
        plot_images['OBV'] = self.save_plot_to_bytes()

        # MACD Plot
        plt.subplot(3, 3, 3)
        plt.plot(adv_stock_data['MACD_12_26_9'], label='MACD')
        plt.plot(adv_stock_data['MACDh_12_26_9'], label='MACD Histogram')
        plt.title('MACD Indicator')
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b%d'))
        plt.xticks(rotation=45, fontsize=8)
        plt.title("MACD")
        plt.legend()
        plot_images['MACD'] = self.save_plot_to_bytes()

        # RSI Plot
        plt.subplot(3, 3, 4)
        plt.plot(adv_stock_data['RSI_14'], label='RSI')
        plt.axhline(y=70, color='r', linestyle='--', label='Overbought (70)')
        plt.axhline(y=30, color='g', linestyle='--', label='Oversold (30)')
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b%d'))
        plt.xticks(rotation=45, fontsize=8)
        plt.title("RSI Indicator")
        plot_images['RSI'] = self.save_plot_to_bytes()

        # Bollinger Bands Plot
        plt.subplot(3, 3, 5)
        plt.plot(adv_stock_data.index, adv_stock_data['BBU_5_2.0'], label='Upper BB')
        plt.plot(adv_stock_data.index, adv_stock_data['BBM_5_2.0'], label='Middle BB')
        plt.plot(adv_stock_data.index, adv_stock_data['BBL_5_2.0'], label='Lower BB')
        plt.plot(adv_stock_data.index, adv_stock_data['Adj Close'], label='Adj Close', color='brown')
        plt.title("Bollinger Bands")
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b%d'))
        plt.xticks(rotation=45, fontsize=8)
        plt.legend()
        plot_images['BB'] = self.save_plot_to_bytes()

        # Stochastc Oscillator Plot
        plt.subplot(3, 3, 6)
        plt.plot(adv_stock_data.index, adv_stock_data['STOCHk_14_3_3'], label='Stoch %K')
        plt.plot(adv_stock_data.index, adv_stock_data['STOCHd_14_3_3'], label='Stoch %D')
        plt.title("Stochastic Oscillator")
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b%d'))
        plt.xticks(rotation=45, fontsize=8)
        plt.legend()
        plot_images['SO'] = self.save_plot_to_bytes()

        # Williams %R Plot
        plt.subplot(3, 3, 7)
        plt.plot(adv_stock_data.index, adv_stock_data['WILLR_14'])
        plt.title("Williams %R")
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b%d'))
        plt.xticks(rotation=45, fontsize=8)
        plot_images['Williams'] = self.save_plot_to_bytes()

        # ADX Plot
        plt.subplot(3, 3, 8)
        plt.plot(adv_stock_data.index, adv_stock_data['ADX_14'])
        plt.title("Average Directional Index (ADX)")
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b%d'))
        plt.xticks(rotation=45, fontsize=8)
        plot_images['ADX'] = self.save_plot_to_bytes()

        # CMF Plot
        plt.subplot(3, 3, 9)
        plt.plot(adv_stock_data.index, adv_stock_data['CMF_20'])
        plt.title("Chaikin Money Flow (CMF)")
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b%d'))
        plt.xticks(rotation=45, fontsize=8)
        plot_images['CMF'] = self.save_plot_to_bytes()

        plt.close()

        return plot_images
