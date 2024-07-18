import logging
import os
import pandas as pd
from datetime import datetime, timedelta
from telegram import (
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    Update,
    InputFile,
)
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CallbackContext,
)
from telegram.error import TelegramError
from backend.scraper import Dataset
from backend.analyzer import Analyzer
from backend.user_database import DB
from backend.predictor import Predictor


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger('prophet').setLevel(logging.ERROR)
logger = logging.getLogger(__name__)

TICKER_LIST = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]
TICKER_LIST = TICKER_LIST.iloc[:, 0].tolist()

notification_log = 'backend/notification_log.txt'

# initializing ----------------------------------------------------------------
db = DB()
db.init_db()
# -----------------------------------------------------------------------------

CHOOSING = range(1)

reply_keyboard = [["Help"],
]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.message.chat_id
    db.add_user(chat_id)

    await context.bot.send_message(chat_id=chat_id,
                                   text=f"Hi! 😊 I'm bot to help you monitor stocks. 📈 You have been subscribed for daily notifications! 🔔\nYou'll be notified when new spikes get caught. 📊",
                                   reply_markup=markup,
    )
    return CHOOSING

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_message(chat_id=update.message.chat_id,
                                   text=f"/start - Launch bot 🚀\n/help - Get list of commands 📋",
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
        file.write(str(datetime.now().date()) + '\n')

async def check_spikes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    for ticker in TICKER_LIST:
        dataset = Dataset(ticker=ticker)
        spike_status = dataset.check_spike()
        if spike_status:
            data = dataset.build_dataset()

            analyzer = Analyzer(ticker=ticker, data=data)
            analyzer.analyze()

            description = analyzer.get_description()
            plot_images = analyzer.make_tech_plots()

            predictor = Predictor(dataset=data)
            forecast = predictor.forecast()
            forecast_description = (f'\n📅 Forecast date: {forecast["forecast_date"]}\n'
                                    f'📈 Forecast (Closing Price): {forecast["forecast"]}\n'
                                    f'❓ Uncertainty: {forecast["bound"]}%\n'
                                    )
            description += forecast_description

            description += (f"\n🏢 About the company:\n"
                            f"🏭 Sector: {dataset.info['sector']}\n"
                            f"🌍 Country: {dataset.info['country']}\n"
                            f"💵 Currency: {dataset.info['currency']}\n"
                            f"🌐 Website: {dataset.info['website']}\n"
                            )

        users = db.get_users()
        for user in users:
            try:
                await context.bot.send_message(chat_id=user,
                                               text=description
                )
                await context.bot.send_photo(chat_id=user,
                                             photo=InputFile(plot_images['PT'])
                )
            except TelegramError as e:
                if "blocked" in str(e).lower():
                    print(f"User {user} has blocked the bot. Removing from database.")
                    db.remove_user(user)
                else:
                    print(f"Failed to send message to {user}: {e}")

    update_notification_log(notification_log)

    return CHOOSING

async def fallback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_message(chat_id=update.message.chat_id,
                                   text=f"Sorry, I didn't understand this command.",
                                   reply_markup=markup,
    )
    return CHOOSING

