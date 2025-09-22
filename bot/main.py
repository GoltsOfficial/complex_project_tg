import os
import asyncio
import feedparser
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
from bot.handlers import handle_message
from bot.db.database import get_all_feeds, seen_links, news_queue, get_all_ads, decrement_ad_view
from bot.states import user_states

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher()

dp.message.register(handle_message)

SEND_INTERVAL = 60  # базовый интервал

# ====================== Фоновые задачи ======================
async def fetch_feeds():
    while True:
        feeds = get_all_feeds()
        for feed in feeds:
            try:
                parsed = feedparser.parse(feed["url"])
                for entry in parsed.entries:
                    if entry.link not in seen_links:
                        seen_links.add(entry.link)
                        news_queue.append({"type": "rss", "entry": entry})
            except Exception as e:
                print(f"Ошибка RSS {feed['url']}: {e}")
        await asyncio.sleep(60)

async def post_news():
    while True:
        if news_queue:
            post = news_queue.pop(0)
            if post["type"] == "rss":
                entry = post["entry"]
                text = f"<b>{entry.title}</b>\n{entry.link}"
            elif post["type"] == "ad":
                ad = post["entry"]
                text = f"📢 Реклама:\n{ad['text']}"
                decrement_ad_view(ad['id'])
            try:
                await bot.send_message(CHANNEL_ID, text)
            except Exception as e:
                print(f"Ошибка отправки: {e}")

        # добавляем рекламу в очередь
        ads = get_all_ads()
        for ad in ads:
            news_queue.append({"type": "ad", "entry": ad})

        await asyncio.sleep(SEND_INTERVAL)

# ====================== Запуск ======================
async def main():
    asyncio.create_task(fetch_feeds())
    asyncio.create_task(post_news())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
