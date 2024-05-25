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
from backend.scraper import Scraper
from backend.tech_analyzer import Analyzer
from backend.user_database import DB

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

SYMBOLS_LIST = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]
# symbols_list = symbols.iloc[:, 0].tolist()
SYMBOLS_LIST = SYMBOLS_LIST.iloc[:10, 0].tolist()

notification_log = 'backend/notification_log.txt'

# initializing ----------------------------------------------------------------
scraper = Scraper(SYMBOLS_LIST)
data = scraper.fetch_data(mode='adj_close')

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
                                   text=f"Hi! I'm bot to help you monitor stocks. You have been registered for daily notifications!.",
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

async def check_spikes(update: Update, context: ContextTypes.DEFAULT_TYPE, mode='manually') -> None:
    skyrockets_data = scraper.check_spike(data=data)
    if skyrockets_data is not False:
        for symbol in skyrockets_data.columns[1:]:
            stock_data = scraper.fetch_data(symbol=str(symbol), mode='stock_data')

            analyzer = Analyzer(symbol=str(symbol), stock_data=stock_data)
            adv_stock_data = analyzer.analyze()
            description = analyzer.get_description(start_date=datetime.now().date() - timedelta(days=1) - timedelta(days=1), # TODO: remove timedelta(days=1). this for testing at night when no data for new day
                                                   end_date=datetime.now().date() - timedelta(days=1),
                                                   adv_stock_data=adv_stock_data)
            plot_images = analyzer.make_tech_plots(adv_stock_data=adv_stock_data)

            if mode == 'manually':
                await context.bot.send_message(chat_id=update.message.chat_id,
                                               text=description,
                )
                await context.bot.send_photo(chat_id=update.message.chat_id,
                                             photo=InputFile(plot_images['PT']),
                )

            elif mode == 'auto':
                # if is_notification_sent_today(notification_log):
                #     return
                users = db.get_users()
                for user in users:
                    await context.bot.send_message(chat_id=user,
                                                   text=description,
                    )
                    await context.bot.send_photo(chat_id=user,
                                                 photo=InputFile(plot_images['PT']),
                    )
                update_notification_log(notification_log)

    return CHOOSING

async def fallback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_message(chat_id=update.message.chat_id,
                                   text=f"Sorry, I didn't understand this command.",
                                   reply_markup=markup,
    )

