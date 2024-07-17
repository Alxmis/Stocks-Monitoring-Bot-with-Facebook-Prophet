import logging
import os
import pandas as pd
from datetime import datetime, timedelta
from telegram import (
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    Update,
    InputFile
)
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CallbackContext,
)
from apscheduler.schedulers.background import BackgroundScheduler
from backend.scraper import Dataset
from backend.tech_analyzer import Analyzer
from backend.user_database import DB
from backend.predictor import Predictor


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

TICKER_LIST = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]
# symbols_list = symbols.iloc[:, 0].tolist()
TICKER_LIST = TICKER_LIST.iloc[:10, 0].tolist()

notification_log = 'backend/notification_log.txt'

# initializing ----------------------------------------------------------------
# scraper = Scraper(SYMBOLS_LIST)

db = DB()
db.init_db()

# -----------------------------------------------------------------------------

# analizer = tech_analyzer.Analyzer()
CHOOSING = range(1)

reply_keyboard = [["Check spikes", "Help"],
]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.message.chat_id
    db.add_user(chat_id)

    await context.bot.send_message(chat_id=chat_id,
                                   text=f"Hi! I'm bot to help you monitor stocks. You have been registered for daily notifications!\nYou'll be notified when new spikes get caught.",
                                   reply_markup=markup,
    )
    return CHOOSING

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_message(chat_id=update.message.chat_id,
                                   text=f"/start - launch bot\n/help - get list of commands\n/spikes - check last great changes in data",
                                   reply_markup=markup,
    )

    return CHOOSING

def is_notification_sent_today(notification_log):
    if not os.path.exists(notification_log):
        return False
    with open(notification_log, 'r') as file:
        last_sent_date = file.read().strip()
    return last_sent_date == str(datetime.now().date())

def update_notification_log(notification_log):
    with open(notification_log, 'a') as file:
        file.write(str(datetime.now().date()))

def predict(ticker) -> dict:
    predictor = Predictor(ticker)
    forecast = predictor.forecast()

    actual_forecast = round(forecast.yhat[0], 2)

    lower_bound = round(forecast.yhat_lower[0], 2)
    upper_bound = round(forecast.yhat_upper[0], 2)
    bound = round(((upper_bound - actual_forecast) + (actual_forecast - lower_bound) / 2), 2)

    # summary = predictor.info["summary"]
    # country = predictor.info["country"]
    # sector = predictor.info["sector"]
    # website = predictor.info["website"]
    # min_date = predictor.info["min_date"]
    # max_date = predictor.info["max_date"]

    forecast_date = predictor.forecast_date.date()
    # print(f"Ticker: {ticker.upper()}")
    # print(f"Sector: {sector}")
    # print(f"Country: {country}")
    # print(f"Website: {website}")
    # print(f"Summary: {summary}")
    # print(f"Min Date: {min_date}")
    # print(f"Max Date: {max_date}")
    # print(f"Forecast Date: {forecast_date}")
    # print(f"Forecast: {actual_forecast}")
    # print(f"Bound: {bound}")

    return {
        'forecast_date': forecast_date,
        'forecast': forecast,
        'bound': bound
    }


async def check_spikes(update: Update, context: ContextTypes.DEFAULT_TYPE, mode='manual') -> None:
    # print(TICKER_LIST)
    for ticker in TICKER_LIST:
        # print(ticker)
        dataset = Dataset(ticker=ticker)
        spike_status = dataset.check_spike()
        if spike_status: # if spike is detected
            data = dataset.build_dataset()
            analyzer = Analyzer(ticker=ticker)
            analyzer.analyze(data)
            description = analyzer.get_description()
            plot_images = analyzer.make_tech_plots()
            predictor = Predictor(dataset=data)
            forecast = predictor.forecast()
            print(forecast)
            print(predictor.forecast_date.date())
            print(dataset.info)
            input()

    return CHOOSING



    data = scraper.fetch_data(mode='adj_close', days=2, interval='1d') # TODO: change days to 2
    # print(data)
    # print(datetime.now().date() - timedelta(days=3) - timedelta(days=1))
    skyrockets_data = scraper.check_spike(data=data)
    # print(skyrockets_data)
    # print(skyrockets_data.dropna(axis=1))
    # print(skyrockets_data.dropna(axis=1).sort_index(axis=1))
    # input()

    if skyrockets_data is not False:
        skyrockets_data = skyrockets_data.dropna(axis=1).sort_index(axis=1)

        for symbol in skyrockets_data.columns[1:]:
            stock_data = scraper.fetch_data(symbol=str(symbol), mode='stock_data', days=30, interval='1h')

            analyzer = Analyzer(symbol=str(symbol), stock_data=stock_data)
            adv_stock_data = analyzer.analyze()

            # recent_stock_price = adv_stock_data.loc[adv_stock_data.index.to_series().dt.date.isin([
            #     # pd.to_datetime(datetime.now().date() - timedelta(days=1)),
            #     pd.to_datetime('2024-05-23').date(),
            #     # pd.to_datetime(datetime.now().date())
            #     pd.to_datetime('2024-05-24').date(),
            # ])].groupby(adv_stock_data.index.to_series().dt.date).tail(1)
            # print(recent_stock_price)
            description = analyzer.get_description(start_date=datetime.now().date() - timedelta(days=3) - timedelta(days=1), # TODO: remove timedelta(days=1). this for testing at night when no data for new day
                                                   end_date=datetime.now().date() - timedelta(days=3),
                                                   adv_stock_data=adv_stock_data
            )
            plot_images = analyzer.make_tech_plots(adv_stock_data=adv_stock_data)

            # Predictions
            stock_price = scraper.fetch_data(symbol=str(symbol), mode='stock_data', days=360, interval='1h') # TODO: days
            predictor = Predictor(stock_price=stock_price)
            predictor.train_model()
            stock_price_forecast = predictor.make_forecast(periods=7) # TODO: periods
            forecast_plot_images = predictor.make_forecast_plot(stock_price_forecast=stock_price_forecast)

            if mode == 'manual':
                await context.bot.send_message(chat_id=update.message.chat_id,
                                               text=description,
                )
                await context.bot.send_photo(chat_id=update.message.chat_id,
                                             photo=InputFile(plot_images['RSI']),
                )
                await context.bot.send_photo(chat_id=update.message.chat_id,
                                               photo=InputFile(forecast_plot_images['forecast_plot'])
                )

            elif mode == 'auto':
                users = db.get_users()
                for user in users:
                    await context.bot.send_message(chat_id=user,
                                                   text=description,
                    )
                    await context.bot.send_photo(chat_id=user,
                                                 photo=InputFile(plot_images['PT']),
                    )
                update_notification_log(notification_log)

    else:
        await update.message.reply_text(text=f"No spikes caught today.",
                                        reply_markup=markup,
        ) # Sent only if spikes are manually checked

    return CHOOSING

async def fallback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_message(chat_id=update.message.chat_id,
                                   text=f"Sorry, I didn't understand this command.",
                                   reply_markup=markup,
    )

