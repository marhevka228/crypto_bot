import os
import logging
import requests
import pandas as pd
import re
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_info_from_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    text = soup.get_text()

    emails = re.findall(r'[\w\.-]+@[\w\.-]+', text)
    wallets = re.findall(r'0x[a-fA-F0-9]{40}|[13][a-km-zA-HJ-NP-Z1-9]{25,34}', text)
    socials = re.findall(r'https?://(?:t\.me|twitter\.com|discord\.gg|discord\.com|instagram\.com|facebook\.com|linkedin\.com)/[\w\-\._]+', text)

    return list(set(emails)), list(set(wallets)), list(set(socials))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Отправь мне ссылку на сайт — я соберу email, кошельки и соцсети, и верну CSV.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    try:
        response = requests.get(url, timeout=10)
        emails, wallets, socials = extract_info_from_html(response.text)

        df = pd.DataFrame({
            'Emails': pd.Series(emails),
            'Wallets': pd.Series(wallets),
            'Socials': pd.Series(socials)
        })

        file_path = 'parsed_data.csv'
        df.to_csv(file_path, index=False)
        await update.message.reply_document(document=open(file_path, 'rb'))

    except Exception as e:
        logger.error(f"Ошибка при обработке URL: {e}")
        await update.message.reply_text("Произошла ошибка при обработке ссылки. Проверь, доступен ли сайт.")

def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.run_polling()

if __name__ == '__main__':
    main()
