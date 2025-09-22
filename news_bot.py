import os
import asyncio
import feedparser
from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from dotenv import load_dotenv

# ====================== Загрузка env ======================
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()

rss_feeds = []
user_states = {}
seen_links = set()
news_queue = []

SEND_INTERVAL = 60

# ====================== Импорт команд ======================
from commands.add_rss import add_rss_handler
from commands.list_rss import list_rss_handler
from commands.edit_rss import edit_rss_handler
from commands.remove_rss import remove_rss_handler

# ====================== Callback handler для кнопок ======================
@dp.callback_query()
async def all_callbacks(callback: types.CallbackQuery):
    await edit_rss_callback_handler(callback, rss_feeds, user_states)

# ====================== Фоновые задачи ======================
async def fetch_feeds():
    while True:
        for feed in rss_feeds:
            parsed = feedparser.parse(feed["url"])
            for entry in parsed.entries:
                if entry.link not in seen_links:
                    seen_links.add(entry.link)
                    news_queue.append(entry)
        await asyncio.sleep(60)


async def post_news():
    while True:
        if news_queue:
            entry = news_queue.pop(0)
            text = f"<b>{entry.title}</b>\n{entry.link}"
            try:
                await bot.send_message(CHANNEL_ID, text)
            except Exception as e:
                print(f"Ошибка отправки: {e}")
        await asyncio.sleep(SEND_INTERVAL)

# ====================== Маршрутизатор команд ======================
async def route_message(message: types.Message):
    chat_id = message.chat.id
    text = message.text.strip()

    # ------------------ Проверка интерактива ------------------
    if chat_id in user_states:
        mode = user_states[chat_id]["mode"]
        state = user_states[chat_id]
        if mode == "add":
            await add_rss_handler(message, rss_feeds, user_states)
            return
        elif mode == "edit":
            if state["step"] == 2:
                # Шаг 2 — ввод нового значения
                await edit_rss_apply_handler(message, rss_feeds, user_states)
            else:
                # Шаг 0 — ввод номера
                await edit_rss_handler(message, rss_feeds, user_states)
            return
        elif mode == "remove":
            await remove_rss_handler(message, rss_feeds, user_states)
            return

    # ------------------ Команды ------------------
    text_lower = text.lower()
    if text_lower == "/add_rss":
        await add_rss_handler(message, rss_feeds, user_states)
    elif text_lower == "/list_rss":
        await list_rss_handler(message, rss_feeds)
    elif text_lower == "/edit_rss":
        await edit_rss_handler(message, rss_feeds, user_states)
    elif text_lower == "/remove_rss":
        await remove_rss_handler(message, rss_feeds, user_states)
    else:
        await message.answer(
            "❌ Неверная команда.\nДоступные команды:\n/add_rss\n/list_rss\n/edit_rss\n/remove_rss"
        )

# ====================== Хэндлер для всех сообщений ======================
@dp.message()
async def all_messages(message: types.Message):
    await route_message(message)

# ====================== Старт ======================
async def main():
    print("🚀 Бот запускается...")
    asyncio.create_task(fetch_feeds())
    asyncio.create_task(post_news())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
