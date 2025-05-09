import os
import logging
import requests
import pandas as pd
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Отправь мне ссылку, и я извлеку данные.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    try:
        response = requests.get(url)
        if url.endswith('.csv'):
            df = pd.read_csv(url)
        else:
            soup = BeautifulSoup(response.text, 'html.parser')
            df = pd.DataFrame({'data': [soup.title.string]})
        file_path = 'data.csv'
        df.to_csv(file_path, index=False)
        await update.message.reply_document(document=open(file_path, 'rb'))
    except Exception as e:
        logger.error(f"Ошибка при обработке URL: {e}")
        await update.message.reply_text("Произошла ошибка при обработке ссылки.")

def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.run_polling()

if __name__ == '__main__':
    main()
