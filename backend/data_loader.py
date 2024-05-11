from scraper import Scraper
import pandas as pd

def initialize_scraper():
    symbols = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]
    # symbols_list = symbols.iloc[:, 0].tolist()
    symbols_list = symbols.iloc[:20, 0].tolist()

    scraper = Scraper(symbols_list)

    raw_data = scraper.fetch_data()
    print(raw_data)
    # TODO: below
    data = pd.concat([
        raw_data[raw_data.index.date == pd.to_datetime('2024-05-09').date()].iloc[[-1]],
        raw_data[raw_data.index.date == pd.to_datetime('2024-05-10').date()].iloc[[-1]]])

    # scraper.make_plot(raw_data, symbol='MMM')


initialize_scraper()