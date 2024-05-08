import logging
from telegram import Update
from telegram.ext import ContextTypes

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)
# logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_message(chat_id=update.effective_chat_id, text=f"Hi! I'm bot to help you monitor stocks.")

# async def start(update: Update, _) -> None:
#     await update.message.reply_text(rf"Hi! I'm bot to help you monitor stocks.")
# # OR
# async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     user = update.effective_user
#     await update.message.reply_html(
#         rf"Hi {user.mention_html()}!"
#     )

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_message(chait_id=update.effective_chat_id, text="\start - launch bot\n/help - get list of commands\n\spikes - check last great changes in data")

async def check_spikes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    ... # TODO

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_message(chat_id=update.effective_chat_id, text="Sorry, I didn't understand this command.")


# TODO: add inline

