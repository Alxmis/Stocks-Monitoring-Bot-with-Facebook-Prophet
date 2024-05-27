import numpy as np
from prophet import Prophet
import matplotlib.pyplot as plt
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from functools import reduce
from io import BytesIO

# TODO: move to another file
import warnings
warnings.filterwarnings('ignore')

class Predictor():
    def __init__(self, stock_price: pd.DataFrame) -> None:
        self.stock_price = stock_price
        self.model = None

    def train_model(self) -> None:
        self.stock_price.index = self.stock_price.index.tz_localize(None)
        self.stock_price = self.stock_price.reset_index().rename(columns={'Datetime': 'ds', 'Adj Close': 'y'})
        self.model = Prophet()
        self.model.add_country_holidays(country_name='US')

        self.model.fit(self.stock_price)

    def make_forecast(self, periods=7) -> pd.DataFrame: # TODO: periods
        future = self.model.make_future_dataframe(periods=periods)
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
        ax = forecast_plot.gca()

        # Adjusting plot scale # TODO: do
        # predicted_lines_len = len(stock_price_forecast) - len(self.stock_price)
        # stock_price_forecast = stock_price_forecast.iloc[-predicted_lines_len:, :]
        # start_x = stock_price_forecast.iloc[0, 0]
        # end_x = stock_price_forecast.iloc[-1, 0]
        # ax.set_xlim(pd.to_datetime([start_x, end_x]))
        # ax.set_ylim([280, 290]) # TODO: adjust y scale

        plot_images['forecast_plot'] = self.save_plot_to_bytes()
        forecast_components_plot = self.model.plot_components(stock_price_forecast)
        plot_images['forecast_components_plot'] = self.save_plot_to_bytes()

        plt.close()
        return plot_images

    # def test_plot(self, stock_price_forecast):
    #     df = pd.merge(self.stock_price, stock_price_forecast, on='ds', how='right')
    #     df.set_index('ds').plot(figsize=(8, 4), color=['royalblue', "#34495e", "#e74c3c", "#e74c3c"], grid=True)
    #     plt.show()

    # def backtesting(self):
    #     self.stock_price['dayname'] = self.stock_price['ds'].dt.day_name()
    #     self.stock_price['month'] = self.stock_price['ds'].dt.month
    #     self.stock_price['year'] = self.stock_price['ds'].dt.year
    #     self.stock_price['month/year'] = self.stock_price['month'].map(str) + '/' + self.stock_price['year'].map(str)
    #
    #     self.stock_price = pd.merge(self.stock_price,
    #                                 self.stock_price['month/year'].drop_duplicates().reset_index(drop=True).reset_index(),
    #                                 on='month/year',
    #                                 how='left')
    #     self.stock_price = self.stock_price.rename(columns={'index': 'month/year_index'})
    #     # print(self.stock_price.tail())
    #
    #     loop_list = self.stock_price['month/year'].unique().tolist()
    #     max_num = len(loop_list) - 1
    #     forecast_frames = []
    #
    #     for num, item in enumerate(loop_list):
    #         if num == max_num:
    #             pass
    #         else:
    #             df = self.stock_price.set_index('ds')[
    #                 self.stock_price[self.stock_price['month/year'] == loop_list[0]]['ds'].min():\
    #                 self.stock_price[self.stock_price['month/year'] == item]['ds'].max()]
    #
    #             df = df.reset_index()[['ds', 'y']]
    #             model = Prophet()
    #             model.fit(df)
    #
    #             future = self.stock_price[self.stock_price['month/year_index'] == (num + 1)][['ds']]
    #             forecast = model.predict(future)
    #             forecast_frames.append(forecast)
    #
    #     stock_price_forecast = reduce(lambda top, bottom: pd.concat([top, bottom], sort=False), forecast_frames)
    #     stock_price_forecast = stock_price_forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]
    #
    #     df = pd.merge(self.stock_price[['ds', 'y', 'month/year_index']], stock_price_forecast, on='ds')
    #     df['Percent Change'] = df['y'].pct_change()
    #     df.set_index('ds')[['y', 'yhat', 'yhat_lower', 'yhat_upper']].plot(figsize=(16, 8), color=['royalblue', "#34495e", "#e74c3c", "#e74c3c"], grid=True)
    #
    #     # ----------------------------------------------------------------
    #     # TRADING ALGOS
    #     df['Hold'] = (df['Percent Change'] + 1).cumprod()
    #     df['Prophet'] = ((df['yhat'].shift(-1) > df['yhat']).shift(1) * (df['Percent Change']) + 1).cumprod()
    #     df['Prophet Thresh'] = ((df['y'] > df['yhat_lower']).shift(1) * (df['Percent Change']) + 1).cumprod()
    #     df['Seasonality'] = ((~df['ds'].dt.month.isin([8, 9])).shift(1) * (df['Percent Change']) + 1).cumprod()
    #
    #     (df.dropna().set_index('ds')[['Hold', 'Prophet', 'Prophet Thresh', 'Seasonality']] * 1000).plot(figsize=(16, 8),
    #                                                                                                     grid=True)
    #
    #     print(f"Hold = {df['Hold'].iloc[-1] * 1000:,.0f}")
    #     print(f"Prophet = {df['Prophet'].iloc[-1] * 1000:,.0f}")
    #     print(f"Prophet Thresh = {df['Prophet Thresh'].iloc[-1] * 1000:,.0f}")
    #     print(f"Seasonality = {df['Seasonality'].iloc[-1] * 1000:,.0f}")
    #
    #
    #     performance = {}
    #
    #     for x in np.linspace(.9, .99, 10):
    #         y = ((df['y'] > df['yhat_lower'] * x).shift(1) * (df['Percent Change']) + 1).cumprod()
    #         performance[x] = y
    #
    #     best_yhat = pd.DataFrame(performance).max().idxmax()
    #     pd.DataFrame(performance).plot(figsize=(16, 8), grid=True);
    #     print(f'Best Yhat = {best_yhat:,.2f}')
    #
    #     df['Optimized Prophet Thresh'] = ((df['y'] > df['yhat_lower'] * best_yhat).shift(1) *
    #                                       (df['Percent Change']) + 1).cumprod()
    #     (df.dropna().set_index('ds')[['Hold', 'Prophet', 'Prophet Thresh',
    #                                   'Seasonality', 'Optimized Prophet Thresh']] * 1000).plot(figsize=(16, 8),
    #                                                                                            grid=True)
    #
    #     print(f"\nHold = {df['Hold'].iloc[-1] * 1000:,.0f}")
    #     print(f"Prophet = {df['Prophet'].iloc[-1] * 1000:,.0f}")
    #     print(f"Prophet Thresh = {df['Prophet Thresh'].iloc[-1] * 1000:,.0f}")
    #     print(f"Seasonality = {df['Seasonality'].iloc[-1] * 1000:,.0f}")
    #     print(f"Optimized Prophet Thresh = {df['Optimized Prophet Thresh'].iloc[-1] * 1000:,.0f}")
    #     # plt.show()



# stock_data = yf.download('AAPL', start='2018-01-01', end='2023-01-01')
# print(stock_data)
# stock_price = stock_data[['Adj Close']]
# predictor = Predictor(stock_price)
# predictor.train_model()
# stock_price_forecast = predictor.make_forecast(periods=5)
# predictor.make_forecast_plot(stock_price_forecast)

# predictor.backtesting(stock_price_forecast)