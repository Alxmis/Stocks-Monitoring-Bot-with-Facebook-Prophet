from dotenv import load_dotenv
import os
import datetime
import pytz

from telegram.ext import (
    filters,
    MessageHandler,
    ApplicationBuilder,
    CommandHandler,
    ConversationHandler
)
from frontend import handler
from frontend.handler import CHOOSING

LOCAL_TIMEZONE = pytz.timezone('Europe/Moscow')

# Loading env variables ----------------------------------------------------------------
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
# --------------------------------------------------------------------------------------


def main() -> None:
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", handler.start)],
        states={
            CHOOSING: [
                MessageHandler(filters.Regex(r"^Help$"), handler.help),
            ],
        },
        fallbacks=[
            MessageHandler(filters.TEXT & ~filters.COMMAND, handler.fallback)
        ]
    )

    application.add_handler(conv_handler)

    job_queue = application.job_queue
    job_queue.run_daily(lambda context: handler.check_spikes(None, context=context),
                        time=datetime.time(hour=23, minute=22, second=30).replace(tzinfo=LOCAL_TIMEZONE),
                        days=(1, 2, 3, 4, 5) # run only in weekdays
    )

    application.run_polling()


if __name__ == '__main__':
    main()