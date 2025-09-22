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

# Простое хранилище в памяти (позже заменим на БД)
rss_feeds = []
user_states = {}
seen_links = set()
news_queue = []

SEND_INTERVAL = 60

# ====================== Импорт команд ======================
from commands.add_rss import add_rss_handler
from commands.list_rss import list_rss_handler
from commands.edit_rss import edit_rss_handler, edit_rss_callback_handler
from commands.remove_rss import remove_rss_handler


# ====================== Callback handler для кнопок ======================
@dp.callback_query()
async def all_callbacks(callback: types.CallbackQuery):
    await edit_rss_callback_handler(callback, rss_feeds, user_states, bot)


# ====================== Фоновые задачи ======================
async def fetch_feeds():
    while True:
        for feed in rss_feeds:
            try:
                parsed = feedparser.parse(feed["url"])
                for entry in parsed.entries:
                    if entry.link not in seen_links:
                        seen_links.add(entry.link)
                        news_queue.append(entry)
            except Exception as e:
                print(f"Ошибка парсинга RSS {feed['url']}: {e}")
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


# ====================== Простой обработчик состояний ======================
async def handle_user_state(message: types.Message):
    chat_id = message.chat.id
    text = message.text.strip()

    if chat_id not in user_states:
        return False

    state = user_states[chat_id]

    # Если пользователь ввел команду - прерываем интерактив
    if text.startswith("/"):
        del user_states[chat_id]
        return False

    # Обработка добавления RSS
    if state.get("mode") == "add":
        await add_rss_handler(message, rss_feeds, user_states)
        return True

    # Обработка редактирования RSS
    elif state.get("mode") == "edit":
        await edit_rss_handler(message, rss_feeds, user_states)
        return True

    # Обработка удаления RSS
    elif state.get("mode") == "remove":
        await remove_rss_handler(message, rss_feeds, user_states)
        return True

    return False


# ====================== Маршрутизатор команд ======================
async def route_message(message: types.Message):
    chat_id = message.chat.id
    text = message.text.strip()

    # Сначала проверяем активные состояния
    if await handle_user_state(message):
        return

    # Обработка команд
    if text == "/add_rss":
        user_states[chat_id] = {"mode": "add", "step": 0}
        await message.answer("🔗 Введите ссылку на RSS:")

    elif text == "/list_rss":
        await list_rss_handler(message, rss_feeds)

    elif text == "/edit_rss":
        user_states[chat_id] = {"mode": "edit", "step": 0}
        await edit_rss_handler(message, rss_feeds, user_states)

    elif text == "/remove_rss":
        user_states[chat_id] = {"mode": "remove", "step": 0}
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