# В начале news_bot/main.py исправьте:
import os
import asyncio
import feedparser
import time
import sys

# Уберите эти строки, они не нужны:
# current_dir = os.path.dirname(os.path.abspath(__file__))
# parent_dir = os.path.dirname(current_dir)
# sys.path.append(parent_dir)

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv

# Исправьте импорты на абсолютные
from news_bot.handlers import cmd_start, cmd_help, handle_message, handle_callback
from news_bot.db.database import (
    get_all_feeds, get_all_ads, decrement_ad_view,
    update_feed_last_posted, update_ad_last_posted, seen_links
)

# ... остальной код без изменений ...

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

# Проверяем наличие переменных окружения
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN not found in environment variables")
if not CHANNEL_ID:
    raise ValueError("CHANNEL_ID not found in environment variables")

CHANNEL_ID = int(CHANNEL_ID)

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()

dp.message.register(cmd_start, Command("start"))
dp.message.register(cmd_help, Command("help"))
dp.message.register(handle_message)
dp.callback_query.register(handle_callback)


# ====================== ФОНОВЫЕ ЗАДАЧИ ======================
async def fetch_feeds():
    while True:
        feeds = get_all_feeds()
        for feed in feeds:
            try:
                parsed = feedparser.parse(feed["url"])
                for entry in parsed.entries:
                    if entry.link not in seen_links:
                        seen_links.add(entry.link)
                        # Вместо очереди сразу проверяем время и публикуем
                        current_time = int(time.time())
                        last_posted = feed.get("last_posted", 0)
                        interval_seconds = feed["interval"] * 60

                        if current_time - last_posted >= interval_seconds:
                            text = f"<b>{entry.title}</b>\n{entry.link}"
                            await bot.send_message(CHANNEL_ID, text)
                            update_feed_last_posted(feed["id"])
                            break  # Постим только одну новость за раз
            except Exception as e:
                print(f"Ошибка RSS {feed['url']}: {e}")
        await asyncio.sleep(30)  # Проверяем каждые 30 секунд


async def post_ads():
    while True:
        try:
            ads = get_all_ads()
            current_time = int(time.time())

            for ad in ads:
                if ad['views'] > 0:
                    last_posted = ad.get("last_posted", 0)
                    interval_seconds = ad["interval"] * 60

                    # Проверяем, пришло ли время публикации
                    if current_time - last_posted >= interval_seconds:
                        # Создаем клавиатуру с кнопкой
                        keyboard = InlineKeyboardMarkup(inline_keyboard=[
                            [InlineKeyboardButton(text=ad['button_text'], url=ad['button_url'])]
                        ])

                        caption = f"<b>{ad['title']}</b>\n\n{ad['description']}"

                        # Публикуем рекламу
                        if ad['photo_url']:
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

                        # Обновляем время и уменьшаем просмотры
                        update_ad_last_posted(ad['id'])
                        decrement_ad_view(ad['id'])
                        print(f"Опубликована реклама: {ad['title']}")

                        # Делаем паузу между постами
                        await asyncio.sleep(5)

        except Exception as e:
            print(f"Ошибка отправки рекламы: {e}")

        # Проверяем каждые 30 секунд
        await asyncio.sleep(30)


# ====================== ЗАПУСК ======================
async def main():
    # Запускаем обе фоновые задачи
    asyncio.create_task(fetch_feeds())
    asyncio.create_task(post_ads())

    print("Бот запущен! Ожидаем публикации по расписанию...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
