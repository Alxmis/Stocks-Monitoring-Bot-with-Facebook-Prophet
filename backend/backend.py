import requests
import pandas as pd

EPS_CHANGE = 0.05


def fetch_data(source):
    response = requests.get(source['url'])
    data = response.json()
    df = pd.DataFrame(data)
    df['Date'] = pd.to_datetime(df['Date'])
    return df

def detect_spikes(df):
    df['Change'] = df['Price'].pct_change()
    spikes = df[df['Change'].abs() > EPS_CHANGE]
    return spikes