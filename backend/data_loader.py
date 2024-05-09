from scraper import Scraper
import pandas as pd

def initialize_scraper():
    tickers = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]
    # tickers_list = tickers.iloc[:, 0].tolist()
    tickers_list = tickers.iloc[:20, 0].tolist()

    scraper = Scraper(tickers_list)

    raw_data = scraper.fetch_data()
    data = pd.concat([
        raw_data[raw_data.index.date == pd.to_datetime('2024-05-07').date()].iloc[[-1]],
        raw_data[raw_data.index.date == pd.to_datetime('2024-05-08').date()].iloc[[-1]]])

