# import front
from telegram.ext import (
    filters, MessageHandler, ApplicationBuilder, CommandHandler
)
from backend import handlers

TOKEN = '6901207494:AAGNaj8JepdE8BxpgJl1XgkctfCeMZ_WRhM'

def main() -> None:
    application = ApplicationBuilder().token(TOKEN).build()

    start_handler = CommandHandler('start', handlers.start)
    help_handler = CommandHandler('help', handlers.help)
    check_spikes = CommandHandler('spikes', handlers.check_spikes)
    unknown_handler = MessageHandler(filters.COMMAND, handlers.unknown)

    application.add_handler(start_handler)
    application.add_handler(help_handler)
    application.add_handler(check_spikes)
    application.add_handler(unknown_handler)

    application.run_polling()

if __name__ == '__main':
    main()