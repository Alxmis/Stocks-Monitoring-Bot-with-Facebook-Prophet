import matplotlib.pyplot as plt, matplotlib.dates as mdates
import pandas as pd
import numpy as np
import yfinance as yf
import pandas_ta as ta
from datetime import datetime, timedelta
# from backend.scraper import Scraper
from io import BytesIO
from backend.predictor import Predictor
from backend.scraper import Dataset

class Analyzer:
    def __init__(self, ticker: str) -> None:
        self.ticker = ticker
    #     self.stock_data = stock_data


    # @staticmethod # TODO: remove?
    def analyze(self, data: pd.DataFrame) -> None:
        adv_data = data.iloc[-2:].copy()
        # self.adv_data = self.stock_data
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

        # last_day_summary = adv_data.iloc[-1][['Close',
        #                                         'MACD_12_26_9', 'MACD_histogram_12_26_9', 'RSI_14', 'BBL_5_2.0',
        #                                         'BBM_5_2.0', 'BBU_5_2.0', 'SMA_20', 'EMA_50', 'OBV_in_million',
        #                                         'STOCHk_14_3_3', 'STOCHd_14_3_3', 'ADX_14', 'WILLR_14', 'CMF_20',
        #                                         'PSARl_0.02_0.2', 'PSARs_0.02_0.2',
        # ]]

        # print('Summary of the last day:')
        # print(last_day_summary)
        self.adv_data = adv_data

    # def get_description(self, start_date: datetime.date, end_date: datetime.date) -> str:
    def get_description(self):
        adv_data = self.adv_data.copy()
        # adv_data = adv_data.loc[adv_data.index.to_series().dt.date.isin([
        #         # pd.to_datetime(datetime.now().date() - timedelta(days=1)), # TODO: uncomment
        #         start_date,
        #         # pd.to_datetime(datetime.now().date())
        #         end_date,
        #     ])].groupby(adv_data.index.to_series().dt.date).tail(1)
        # adv_data.index = adv_data.index.date

        # start_date = start_date.strftime('%Y-%m-%d')
        # end_date = end_date.strftime('%Y-%m-%d')
        start_date = adv_data.index[0]
        end_date = adv_data.index[1]
        # start_date = adv_data.reset_index().iloc[0, 1]#.strftime('%Y-%m-%d')
        # end_date = adv_data.reset_index().iloc[1, 1]#.strftime('%Y-%m-%d')
        # adv_data = adv_data.reset_index()

        # start_price = adv_data.loc[start_date, 'Adj Close']
        # end_price = adv_data.loc[end_date, 'Adj Close']
        start_price = adv_data.loc[start_date, 'Close']
        end_price = adv_data.loc[end_date, 'Close']
        price_change = (end_price - start_price) / start_price

        start_volume = adv_data.loc[start_date, 'Volume']
        end_volume = adv_data.loc[end_date, 'Volume']
        volume_change = (end_volume - start_volume) / start_volume

        price_directions = {1: "выросла", -1: "упала", 0: None}
        volume_directions = {1: "увеличился", -1: "уменьшился", 0: None}

        price_change_direction = price_directions[np.sign(price_change)]
        volume_change_direction = volume_directions[np.sign(volume_change)]

        description = f"Зафиксирован скачок в цене акции {self.ticker}. Дата: {adv_data.reset_index().iloc[1, 1].strftime('%Y-%m-%d')}.\n"
        if price_change_direction:
            description += f"Цена {price_change_direction} на {abs(price_change * 100):.2f}%.\n"
        if volume_change_direction:
            description += f"Объем торгов {volume_change_direction} на {abs(volume_change * 100):.2f}%.\n"
        print(description)

        # description += "\nТехнические индикаторы:\n"
        # description += f"RSI: {adv_data.loc[end_date, 'RSI_14']}\n"
        # description += f"MACD: {adv_data.loc[end_date, 'MACD_12_26_9']}\n"
        ... # TODO: add other indicators

        return description


    @staticmethod
    def save_plot_to_bytes() -> bytes:
        buf = BytesIO()
        plt.savefig(buf, format='png', dpi=300)
        buf.seek(0)
        return buf.getvalue()

    # TODO
    def draw_price_curve(self, data: pd.DataFrame, ax: plt.Axes) -> plt.Axes:
        data.plot(ax=ax, color='orange')
        # plt.title(f"Adjusted Close Price of {ticker}", fontsize=16)
        plt.ylabel('Price', fontsize=14)
        plt.xlabel('Time', fontsize=14)
        plt.grid(which="major", color='white', linestyle='-.', linewidth=0.5)

        return ax

    def make_tech_plots(self) -> dict:
        plot_images = {}

        columns = self.adv_data.columns

        # Price Trend Chart
        plt.figure()
        plt.plot(self.adv_data.index, self.adv_data['Close'], label='CClose', color='blue')
        # plt.plot(self.adv_data.index, self.adv_data['EMA_50'], label='EMA 50', color='green')
        # plt.plot(self.adv_data.index, self.adv_data['SMA_20'], label='SMA 20', color='orange')
        plt.title(f"Price Trend of {self.ticker}")
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b%d'))
        plt.xticks(rotation=45, fontsize=8)
        plt.legend()
        plot_images['PT'] = self.save_plot_to_bytes()

        # On-Balance Volume Chart
        if 'OBV' in columns:
            plt.figure()
            plt.plot(self.adv_data['OBV'], label='On-Balance Volume')
            plt.title(f"On-Balance Volume (OBV) Indicator of {self.ticker}")
            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b%d'))
            plt.xticks(rotation=45, fontsize=8)
            plt.legend()
            plot_images['OBV'] = self.save_plot_to_bytes()

        # # MACD Plot
        # if {'MACD_12_26_9', 'MACD_histogram_12_26_9'}.issubset(columns):
        #     plt.figure()
        #     plt.plot(self.adv_data['MACD_12_26_9'], label='MACD')
        #     plt.plot(self.adv_data['MACD_histogram_12_26_9'], label='MACD Histogram')
        #     plt.title(f"MACD Indicator of {self.ticker}")
        #     plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b%d'))
        #     plt.xticks(rotation=45, fontsize=8)
        #     plt.title("MACD")
        #     plt.legend()
        #     plot_images['MACD'] = self.save_plot_to_bytes()
        #
        # # RSI Plot
        # if 'RSI_14' in columns:
        #     plt.figure()
        #     plt.plot(self.adv_data['RSI_14'], label='RSI')
        #     plt.axhline(y=70, color='r', linestyle='--', label='Overbought (70)')
        #     plt.axhline(y=30, color='g', linestyle='--', label='Oversold (30)')
        #     plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b%d'))
        #     plt.xticks(rotation=45, fontsize=8)
        #     plt.title(f"RSI Indicator of {self.ticker}")
        #     plot_images['RSI'] = self.save_plot_to_bytes()
        #
        # # Bollinger Bands Plot
        # if {'BBU_5_2.0', 'BBM_5_2.0', 'BBL_5_2.0'}.issubset(columns):
        #     plt.figure()
        #     plt.plot(self.adv_data.index, self.adv_data['BBU_5_2.0'], label='Upper BB')
        #     plt.plot(self.adv_data.index, self.adv_data['BBM_5_2.0'], label='Middle BB')
        #     plt.plot(self.adv_data.index, self.adv_data['BBL_5_2.0'], label='Lower BB')
        #     plt.plot(self.adv_data.index, self.adv_data['Adj Close'], label='Adj Close', color='brown')
        #     plt.title(f"Bollinger Bands of {self.ticker}")
        #     plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b%d'))
        #     plt.xticks(rotation=45, fontsize=8)
        #     plt.legend()
        #     plot_images['BB'] = self.save_plot_to_bytes()
        #
        # # Stochastic Oscillator Plot
        # if {'STOCHk_14_3_3', 'STOCHd_14_3_3'}.issubset(columns):
        #     plt.figure()
        #     plt.plot(self.adv_data.index, self.adv_data['STOCHk_14_3_3'], label='Stoch %K')
        #     plt.plot(self.adv_data.index, self.adv_data['STOCHd_14_3_3'], label='Stoch %D')
        #     plt.title(f"Stochastic Oscillator of {self.ticker}")
        #     plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b%d'))
        #     plt.xticks(rotation=45, fontsize=8)
        #     plt.legend()
        #     plot_images['SO'] = self.save_plot_to_bytes()
        #
        # # Williams %R Plot
        # if 'WILLR_14' in columns:
        #     plt.figure()
        #     plt.plot(self.adv_data.index, self.adv_data['WILLR_14'])
        #     plt.title(f"Williams %R of {self.ticker}")
        #     plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b%d'))
        #     plt.xticks(rotation=45, fontsize=8)
        #     plot_images['Williams'] = self.save_plot_to_bytes()
        #
        # # ADX Plot
        # if 'ADX_14' in columns:
        #     plt.figure()
        #     plt.plot(self.adv_data.index, self.adv_data['ADX_14'])
        #     plt.title(f"Average Directional Index (ADX) of {self.ticker}")
        #     plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b%d'))
        #     plt.xticks(rotation=45, fontsize=8)
        #     plot_images['ADX'] = self.save_plot_to_bytes()
        #
        # # CMF Plot
        # if 'CMF_20':
        #     plt.figure()
        #     plt.plot(self.adv_data.index, self.adv_data['CMF_20'])
        #     plt.title(f"Chaikin Money Flow (CMF) of {self.ticker}")
        #     plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b%d'))
        #     plt.xticks(rotation=45, fontsize=8)
        #     plot_images['CMF'] = self.save_plot_to_bytes()

        plt.close()
        return plot_images


# scraper = Scraper(['DIS'])
# stock_data = scraper.fetch_data(mode='stock_data')
# print(stock_data)
# analyser = Analyzer('DIS', stock_data)
# self.adv_data = analyser.analyze()
# print(self.adv_data)
# description = analyser.get_description(start_date=datetime.now().date() - timedelta(days=2), end_date=datetime.now().date() - timedelta(days=1), self.adv_data=self.adv_data)
# description = analyser.get_description(start_date='2024-05-16', end_date='2024-05-17', self.adv_data=self.adv_data)
# print(description)
# print((datetime.now().date() - timedelta(days=1)).strftime('%Y-%m-%d'))
# analyser.make_tech_plots(self.adv_data)

# predictor = Predictor(stock_data)
# predictor.train_model()
# print(predictor.make_forecast())
# print(stock_data)