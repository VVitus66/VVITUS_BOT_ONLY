import os
import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(level=logging.INFO)
TOKEN = os.environ.get('TELEGRAM_TOKEN')

# Файл с курсом от парсера
RATE_FILE = 'current_rate.txt'

def get_rate():
    try:
        with open(RATE_FILE, 'r') as f:
            return float(f.readline().strip())
    except:
        return 77.0

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [KeyboardButton("💰 Купить USDT"), KeyboardButton("💸 Продать USDT")],
        [KeyboardButton("📊 Курс"), KeyboardButton("📋 Мои заявки")],
        [KeyboardButton("❓ Помощь")]
    ]
    await update.message.reply_text(
        "🤖 *VVITUS EXCHANGE*\n\n"
        "Покупка и продажа USDT (TRC20) по лучшему курсу!\n\n"
        "Выберите действие:",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True),
        parse_mode="Markdown"
    )

async def kurs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    base = get_rate()
    buy_price = base * 1.0      # Покупка USDT у клиента (ты отдаёшь рубли)
    sell_price = base * 1.06    # Продажа USDT клиенту (клиент отдаёт рубли)
    
    await update.message.reply_text(
        f"📊 *Курс USDT (TRC20)*\n\n"
        f"💰 Покупка: *{buy_price:.2f}* RUB\n"
        f"💸 Продажа: *{sell_price:.2f}* RUB\n\n"
        f"🔄 Обновляется каждые 5 минут",
        parse_mode="Markdown"
    )

async def buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💰 *Покупка USDT*\n\n"
        "Сколько RUB вы хотите обменять?\n"
        "Минимальная сумма: 1000 RUB\n\n"
        "Введите сумму:",
        parse_mode="Markdown"
    )
    context.user_data['action'] = 'buy'

async def sell(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💸 *Продажа USDT*\n\n"
        "Сколько USDT вы хотите продать?\n"
        "Минимальная сумма: 10 USDT\n\n"
        "Введите сумму:",
        parse_mode="Markdown"
    )
    context.user_data['action'] = 'sell'

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "❓ *Помощь*\n\n"
        "1. Нажмите «Купить USDT» или «Продать USDT»\n"
        "2. Введите сумму\n"
        "3. Следуйте инструкциям бота\n\n"
        "По вопросам: @ваш_логин",
        parse_mode="Markdown"
    )

async def my_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📋 У вас пока нет активных заявок.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    action = context.user_data.get('action')
    
    if action == 'buy':
        try:
            rub = float(text)
            if rub < 1000:
                await update.message.reply_text("❌ Минимальная сумма 1000 RUB")
                return
            base = get_rate()
            usdt = rub / (base * 1.06)
            await update.message.reply_text(
                f"✅ Вы получите: *{usdt:.2f} USDT*\n\n"
                f"💳 Реквизиты для оплаты:\n"
                f"`ВАШ_НОМЕР_КАРТЫ`\n\n"
                f"После оплаты нажмите /done",
                parse_mode="Markdown"
            )
        except:
            await update.message.reply_text("❌ Введите число")
        context.user_data['action'] = None
    elif action == 'sell':
        try:
            usdt = float(text)
            if usdt < 10:
                await update.message.reply_text("❌ Минимальная сумма 10 USDT")
                return
            base = get_rate()
            rub = usdt * base
            await update.message.reply_text(
                f"✅ Вы получите: *{rub:.2f} RUB*\n\n"
                f"📤 Отправьте USDT на адрес:\n"
                f"`ВАШ_USDT_КОШЕЛЁК_TRC20`\n\n"
                f"После отправки нажмите /done",
                parse_mode="Markdown"
            )
        except:
            await update.message.reply_text("❌ Введите число")
        context.user_data['action'] = None
    else:
        await update.message.reply_text("Используйте кнопки меню.")

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.Text("💰 Купить USDT"), buy))
    app.add_handler(MessageHandler(filters.Text("💸 Продать USDT"), sell))
    app.add_handler(MessageHandler(filters.Text("📊 Курс"), kurs))
    app.add_handler(MessageHandler(filters.Text("📋 Мои заявки"), my_orders))
    app.add_handler(MessageHandler(filters.Text("❓ Помощь"), help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("✅ Основной бот запущен")
    app.run_polling()

if __name__ == "__main__":
    main()