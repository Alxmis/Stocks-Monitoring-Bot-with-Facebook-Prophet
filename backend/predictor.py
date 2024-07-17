from datetime import datetime, timedelta
import yfinance as yf
import pandas as pd
import prophet
import matplotlib.pyplot as plt


class Dataset:
    def build_dataset(self):
        start_date = datetime(2010, 1, 1).date()
        end_date = datetime.now().date()

        try:
            self.dataset = self.socket.history(start=start_date, end=end_date, interval="1d").reset_index()
            self.dataset.drop(columns=["Dividends", "Stock Splits", "Volume"], inplace=True)
            self.add_forecast_date()
        except Exception as e:
            print("Exception raised at: 'predictor.Dataset.build()", e)
            return False
        else:
            return True

    def add_forecast_date(self):
        present_date = self.dataset.Date.max()
        day_number = pd.to_datetime(present_date).isoweekday()
        if day_number in [5, 6]:
            self.forecast_date = present_date + timedelta(days=(7 - day_number) + 1)
        else:
            self.forecast_date = present_date  + timedelta(days=1)
        print("Valid forcast date: ", self.forecast_date)
        test_row = pd.DataFrame([[self.forecast_date, 0.0, 0.0, 0.0, 0.0]], columns=self.dataset.columns)
        self.dataset = pd.concat([self.dataset, test_row])

class Features(Dataset):
    def create_features(self):
        status = self.build_dataset()
        if status:
            self.create_lag_features()
            self.impute_missing_values()
            self.dataset.drop(columns=["Open", "High", "Low"], inplace=True)
            print(self.dataset.tail(3))
            return True
        else:
            raise Exception("Dataset creation failed.")

    def create_lag_features(self, periods=12):
        for i in range(1, periods + 1):
            self.dataset[f"Close_lag_{i}"] = self.dataset.Close.shift(periods=i, axis=0)
            self.dataset[f"Open_lag_{i}"] = self.dataset.Open.shift(periods=i, axis=0)
            self.dataset[f"High_lag_{i}"] = self.dataset.High.shift(periods=i, axis=0)
            self.dataset[f"Low_lag_{i}"] = self.dataset.Low.shift(periods=i, axis=0)
        return True

    def impute_missing_values(self):
        self.dataset.fillna(0, inplace=True)
        self.info["min_date"] = self.dataset.Date.min().date()
        self.info["max_date"] = self.dataset.Date.max().date() - timedelta(days=1)
        return True

class Predictor(Features):
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

    def build_model(self):
        additional_features = [col for col in self.dataset.columns if "lag" in col]
        try:
            self.model = prophet.Prophet(yearly_seasonality=True, weekly_seasonality=True, seasonality_mode="additive")
            for name in additional_features:
                self.model.add_regressor(name)
        except Exception as e:
            print("Exception raised at: 'predictor.Prophet.build()", e)
            return False
        else:
            return True

    def train_and_forecast(self):
        self.dataset['Date'] = self.dataset['Date'].dt.tz_localize(None)
        self.model.fit(df=self.dataset.iloc[:-1, :].rename(columns={"Date": "ds", "Close": "y"}))
        return self.model.predict(
            self.dataset.iloc[-1:][[col for col in self.dataset if col != "Close"]].rename(columns={"Date": "ds"}))

    def forecast(self):
        self.create_features()
        self.build_model()
        return self.train_and_forecast()

    # def plot_predictions(self, data, forecast):
    #     plt.figure(figsize=(10, 6))
    #     plt.plot(data['Date'], data['Close'], label='Actual Close Prices')
    #     plt.plot(forecast['ds'], forecast['yhat'], label='Forecasted Close Prices')
    #     plt.fill_between(forecast['ds'], forecast['yhat_lower'], forecast['yhat_upper'], color='gray', alpha=0.2,
    #                      label='Confidence Interval')
    #     plt.xlabel('Date')
    #     plt.ylabel('Close Price')
    #     plt.title(f'Actual and Forecasted Close Prices for {self.ticker}')
    #     plt.legend()
    #     plt.show()


# Example usage
# predictor = StockPredictor('AAPL')
# data, predictions = predictor.train_n_predict()
# predictor.plot_predictions(data, predictions)

ticker = 'MSFT'
master_prophet = Predictor(ticker)
forecast = master_prophet.forecast()

actual_forecast = round(forecast.yhat[0], 2)
lower_bound = round(forecast.yhat_lower[0], 2)
upper_bound = round(forecast.yhat_upper[0], 2)
bound = round(((upper_bound - actual_forecast) + (actual_forecast - lower_bound) / 2), 2)

summary = master_prophet.info["summary"]
country = master_prophet.info["country"]
sector = master_prophet.info["sector"]
website = master_prophet.info["website"]
min_date = master_prophet.info["min_date"]
max_date = master_prophet.info["max_date"]

forecast_date = master_prophet.forecast_date.date()
print(f"Ticker: {ticker.upper()}")
print(f"Sector: {sector}")
print(f"Country: {country}")
print(f"Website: {website}")
print(f"Summary: {summary}")
print(f"Min Date: {min_date}")
print(f"Max Date: {max_date}")
print(f"Forecast Date: {forecast_date}")
print(f"Forecast: {actual_forecast}")
print(f"Bound: {bound}")
