import os
import asyncio
import feedparser
import time
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from news_bot.handlers import cmd_start, cmd_help, handle_message, handle_callback
from news_bot.db.database import (
    get_all_feeds, get_all_ads, decrement_ad_view,
    update_feed_last_posted, update_ad_last_posted, seen_links
)

# ⚡ ПЕРЕМЕННЫЕ NEWS BOT - замени эти значения в Railway
BOT_TOKEN = "8164673641:AAG-FDcj1RNvMCxCuOme95YHwEutqZW5NWc"  # Токен news бота
CHANNEL_ID = -1003068329793  # ID канала (замени на свой)

# Проверяем наличие переменных
if BOT_TOKEN == "YOUR_NEWS_BOT_TOKEN_HERE":
    raise ValueError("❌ NEWS_BOT_TOKEN not set! Please set it in Railway variables")

# Инициализация бота
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()

# Регистрация обработчиков
dp.message.register(cmd_start, Command("start"))
dp.message.register(cmd_help, Command("help"))
dp.message.register(handle_message)
dp.callback_query.register(handle_callback)


# ====================== ФОНОВЫЕ ЗАДАЧИ ======================
async def fetch_feeds():
    """Фоновая задача для публикации RSS новостей"""
    while True:
        feeds = get_all_feeds()
        for feed in feeds:
            try:
                parsed = feedparser.parse(feed["url"])
                for entry in parsed.entries:
                    if entry.link not in seen_links:
                        seen_links.add(entry.link)
                        current_time = int(time.time())
                        last_posted = feed.get("last_posted", 0)
                        interval_seconds = feed["interval"] * 60

                        if current_time - last_posted >= interval_seconds:
                            text = f"📰 <b>{entry.title}</b>\n\n{entry.link}"
                            await bot.send_message(CHANNEL_ID, text)
                            update_feed_last_posted(feed["id"])
                            break
            except Exception as e:
                print(f"❌ RSS ошибка {feed['url']}: {e}")
        await asyncio.sleep(30)


async def post_ads():
    """Фоновая задача для публикации рекламы"""
    while True:
        try:
            ads = get_all_ads()
            current_time = int(time.time())

            for ad in ads:
                if ad['views'] > 0:
                    last_posted = ad.get("last_posted", 0)
                    interval_seconds = ad["interval"] * 60

                    if current_time - last_posted >= interval_seconds:
                        keyboard = InlineKeyboardMarkup(inline_keyboard=[
                            [InlineKeyboardButton(text=ad['button_text'], url=ad['button_url'])]
                        ])

                        caption = f"<b>{ad['title']}</b>\n\n{ad['description']}"

                        if ad['photo_url'] and ad['photo_url'].startswith('http'):
                            await bot.send_photo(
                                CHANNEL_ID,
                                photo=ad['photo_url'],
                                caption=caption,
                                reply_markup=keyboard
                            )
                        else:
                            await bot.send_message(
                                CHANNEL_ID,
                                caption,
                                reply_markup=keyboard
                            )

                        update_ad_last_posted(ad['id'])
                        decrement_ad_view(ad['id'])
                        print(f"✅ Опубликована реклама: {ad['title']}")
                        await asyncio.sleep(5)

        except Exception as e:
            print(f"❌ Ошибка отправки рекламы: {e}")

        await asyncio.sleep(30)


# ====================== ЗАПУСК ======================
async def main():
    asyncio.create_task(fetch_feeds())
    asyncio.create_task(post_ads())

    print("🚀 News Bot запущен! Ожидаем публикации...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())