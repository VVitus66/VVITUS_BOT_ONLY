import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

logging.basicConfig(level=logging.INFO)
TOKEN = os.environ.get('TELEGRAM_TOKEN')

if not TOKEN:
    raise ValueError("Токен не найден")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ VVITUS EXCHANGE БОТ РАБОТАЕТ!")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    print("✅ Бот запущен, жду сообщения...")
    app.run_polling()

if __name__ == "__main__":
    main()
