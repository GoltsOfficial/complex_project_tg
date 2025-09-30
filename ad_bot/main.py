import asyncio
import logging
import sqlite3
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command  # <-- Добавьте этот импорт
from aiogram.types import (  # <-- Добавьте этот импорт для клавиатур и платежей
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    LabeledPrice
)

# ⚡ ПЕРЕМЕННЫЕ AD BOT - замени эти значения в Railway
AD_BOT_TOKEN = "8222866315:AAFkZW560q7bkQkRQsto5GA6FP4JSihHNbE"  # Токен ad бота
PROVIDER_TOKEN = "1744374395:TEST:3e689d9dea8c18ad5daf"  # Платежный провайдер
CURRENCY = "RUB"
PRICE_PER_MONTH_RUB = 500
DATABASE_PATH = "payments.db"

# Проверяем токен
if AD_BOT_TOKEN == "YOUR_AD_BOT_TOKEN_HERE":
    raise ValueError("❌ AD_BOT_TOKEN not set! Please set it in Railway variables")

# Инициализация бота и диспетчера
bot = Bot(token=AD_BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()


# Инициализация БД
def init_db():
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS payments
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER NOT NULL,
                  amount INTEGER NOT NULL,
                  currency TEXT NOT NULL,
                  status TEXT DEFAULT 'pending',
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()


# Простые обработчики для ad bot
@dp.message(Command("start"))
async def cmd_start(message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💰 Купить рекламу", callback_data="buy_ad")],
        [InlineKeyboardButton(text="📊 Мои покупки", callback_data="my_orders")]
    ])

    await message.answer(
        f"🤖 <b>Бот для покупки рекламы</b>\n\n"
        f"Стоимость: {PRICE_PER_MONTH_RUB} {CURRENCY} за месяц\n\n"
        "Выберите действие:",
        reply_markup=keyboard
    )


@dp.callback_query(lambda c: c.data == "buy_ad")
async def process_buy_ad(callback):
    prices = [LabeledPrice(label="Рекламный пост (1 месяц)", amount=PRICE_PER_MONTH_RUB * 100)]

    await bot.send_invoice(
        chat_id=callback.message.chat.id,
        title="Рекламный пост",
        description="Размещение рекламного поста в канале на 1 месяц",
        payload="ad_payment",
        provider_token=PROVIDER_TOKEN,
        currency=CURRENCY.lower(),
        prices=prices
    )


async def main():
    init_db()
    try:
        await dp.start_polling(bot, skip_updates=False)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())