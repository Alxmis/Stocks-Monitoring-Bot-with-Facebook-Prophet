from scraper import Scraper
import pandas as pd
from datetime import datetime, timedelta

def initialize_scraper():
    scraper = Scraper(symbols_list)

    raw_data = scraper.fetch_data()
    print(raw_data)
    # TODO: below
    data = pd.concat([
        raw_data[raw_data.index.date == pd.to_datetime('2024-05-09').date()].iloc[[-1]],
        raw_data[raw_data.index.date == pd.to_datetime('2024-05-10').date()].iloc[[-1]]])
    # data = pd.concat([
    #     raw_data[raw_data.index.date == pd.to_datetime(datetime.now().date() - timedelta(days=1))].iloc[[-1]],
    #     raw_data[raw_data.index.date == pd.to_datetime(datetime.now().date())].iloc[[-1]]])


    # scraper.make_plot(raw_data, symbol='MMM')


initialize_scraper()