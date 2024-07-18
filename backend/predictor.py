import pandas as pd
import prophet
from datetime import timedelta

class Features:
    def __init__(self, dataset):
        self.dataset = dataset.copy().drop(columns=["Dividends", "Stock Splits", "Volume"])
        self.info = {}

    def add_forecast_date(self):
        present_date = self.dataset.Date.max()
        day_number = pd.to_datetime(present_date).isoweekday()
        if day_number in [5, 6]:
            self.forecast_date = present_date + timedelta(days=(7 - day_number) + 1)
        else:
            self.forecast_date = present_date + timedelta(days=1)
        test_row = pd.DataFrame([[self.forecast_date, 0.0, 0.0, 0.0, 0.0]], columns=self.dataset.columns)
        self.dataset = pd.concat([self.dataset, test_row])

    def create_features(self):
        self.add_forecast_date()
        try:
            self.create_lag_features()
            self.impute_missing_values()
            self.dataset.drop(columns=["Open", "High", "Low"], inplace=True)
            return True
        except Exception as e:
            print("Exception raised at: 'predictor.features.create_futures()'", e)

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
    def build_model(self):
        additional_features = [col for col in self.dataset.columns if "lag" in col]
        try:
            self.model = prophet.Prophet(yearly_seasonality=True, weekly_seasonality=True, seasonality_mode="additive")
            for name in additional_features:
                self.model.add_regressor(name)
        except Exception as e:
            print("Exception raised at: 'predictor.Prophet.build()'", e)
            return False
        else:
            return True

    def train_and_forecast(self):
        self.dataset['Date'] = self.dataset['Date'].dt.tz_localize(None)
        self.model.fit(df=self.dataset.iloc[:-1, :].rename(columns={"Date": "ds", "Close": "y"}))
        return self.model.predict(
            self.dataset.iloc[-1:][[col for col in self.dataset if col != "Close"]].rename(columns={"Date": "ds"}))

    def forecast(self) -> dict:
        self.create_features()
        self.build_model()
        forecast = self.train_and_forecast()

        actual_forecast = round(forecast.yhat[0], 2)
        lower_bound = round(forecast.yhat_lower[0], 2)
        upper_bound = round(forecast.yhat_upper[0], 2)
        bound = round(((upper_bound - actual_forecast) + (actual_forecast - lower_bound) / 2), 2)
        return {'forecast': actual_forecast,
                'forecast_date': self.forecast_date.date(),
                'bound': bound
        }