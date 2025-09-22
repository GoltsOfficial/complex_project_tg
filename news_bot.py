# ====================== news_bot.py ======================
import os
import asyncio
import sqlite3
import feedparser
from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()

# SQLite база данных
def init_db():
    conn = sqlite3.connect('rss.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS rss_feeds
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL,
                  url TEXT NOT NULL,
                  interval INTEGER DEFAULT 60)''')
    conn.commit()
    conn.close()

def get_all_feeds():
    conn = sqlite3.connect('rss.db')
    c = conn.cursor()
    c.execute("SELECT * FROM rss_feeds")
    feeds = [{"id": row[0], "name": row[1], "url": row[2], "interval": row[3]} for row in c.fetchall()]
    conn.close()
    return feeds

def add_feed(name, url, interval):
    conn = sqlite3.connect('rss.db')
    c = conn.cursor()
    c.execute("INSERT INTO rss_feeds (name, url, interval) VALUES (?, ?, ?)", (name, url, interval))
    conn.commit()
    conn.close()

def update_feed(feed_id, field, value):
    conn = sqlite3.connect('rss.db')
    c = conn.cursor()
    c.execute(f"UPDATE rss_feeds SET {field} = ? WHERE id = ?", (value, feed_id))
    conn.commit()
    conn.close()

def delete_feed(feed_id):
    conn = sqlite3.connect('rss.db')
    c = conn.cursor()
    c.execute("DELETE FROM rss_feeds WHERE id = ?", (feed_id,))
    conn.commit()
    conn.close()

init_db()

user_states = {}
seen_links = set()
news_queue = []
SEND_INTERVAL = 60

# ====================== Команды ======================
@dp.message()
async def handle_message(message: types.Message):
    chat_id = message.chat.id
    text = message.text.strip()

    if chat_id in user_states:
        await handle_user_state(message)
        return

    if text == "/start":
        await message.answer("🤖 RSS Bot\nКоманды: /add_rss /list_rss /edit_rss /remove_rss")

    elif text == "/add_rss":
        user_states[chat_id] = {"mode": "add", "step": 1}
        await message.answer("🔗 Введите ссылку RSS:")

    elif text == "/list_rss":
        feeds = get_all_feeds()
        if not feeds:
            await message.answer("📭 Список RSS пуст.")
            return
        text = "📃 RSS ленты:\n" + "\n".join(f"ID: {f['id']} | {f['name']} | {f['interval']}мин" for f in feeds)
        await message.answer(text)

    elif text == "/edit_rss":
        feeds = get_all_feeds()
        if not feeds:
            await message.answer("📭 Список RSS пуст.")
            return
        user_states[chat_id] = {"mode": "edit", "step": 1}
        text = "📃 Выберите ID RSS:\n" + "\n".join(f"ID: {f['id']} - {f['name']}" for f in feeds)
        await message.answer(text)

    elif text == "/remove_rss":
        feeds = get_all_feeds()
        if not feeds:
            await message.answer("📭 Список RSS пуст.")
            return
        user_states[chat_id] = {"mode": "remove", "step": 1}
        text = "🗑 Выберите ID RSS для удаления:\n" + "\n".join(f"ID: {f['id']} - {f['name']}" for f in feeds)
        await message.answer(text)

    else:
        await message.answer("❌ Неверная команда.")

async def handle_user_state(message: types.Message):
    chat_id = message.chat.id
    text = message.text.strip()
    state = user_states[chat_id]

    if text.startswith("/"):
        del user_states[chat_id]
        return

    if state["mode"] == "add":
        if state["step"] == 1:
            state["url"] = text
            state["step"] = 2
            await message.answer("📝 Введите название:")
        elif state["step"] == 2:
            state["name"] = text
            state["step"] = 3
            await message.answer("⏱ Интервал в минутах:")
        elif state["step"] == 3:
            try:
                interval = int(text)
                add_feed(state["name"], state["url"], interval)
                await message.answer(f"✅ RSS добавлен!\nID: {get_all_feeds()[-1]['id']}\nНазвание: {state['name']}\nИнтервал: {interval}мин")
                del user_states[chat_id]
            except:
                await message.answer("❌ Введите число:")

    elif state["mode"] == "edit":
        if state["step"] == 1:
            try:
                feed_id = int(text)
                feeds = get_all_feeds()
                feed = next((f for f in feeds if f['id'] == feed_id), None)
                if feed:
                    state["feed_id"] = feed_id
                    state["step"] = 2
                    await message.answer(f"✏️ Редактирование: {feed['name']}\nЧто меняем?\n1. Название\n2. Ссылка\n3. Интервал")
                else:
                    await message.answer("❌ Неверный ID.")
            except:
                await message.answer("❌ Введите число ID:")
        elif state["step"] == 2:
            if text in ["1", "2", "3"]:
                state["field"] = ["name", "url", "interval"][int(text)-1]
                state["step"] = 3
                await message.answer(f"Введите новое значение для {state['field']}:")
            else:
                await message.answer("❌ Введите 1, 2 или 3")
        elif state["step"] == 3:
            try:
                value = int(text) if state["field"] == "interval" else text
                update_feed(state["feed_id"], state["field"], value)
                await message.answer(f"✅ {state['field']} обновлен!")
                del user_states[chat_id]
            except:
                await message.answer("❌ Ошибка обновления")

    elif state["mode"] == "remove":
        if state["step"] == 1:
            try:
                feed_id = int(text)
                feeds = get_all_feeds()
                feed = next((f for f in feeds if f['id'] == feed_id), None)
                if feed:
                    delete_feed(feed_id)
                    await message.answer(f"✅ RSS удален: {feed['name']}")
                    del user_states[chat_id]
                else:
                    await message.answer("❌ Неверный ID.")
            except:
                await message.answer("❌ Введите число ID:")

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
                        news_queue.append(entry)
            except Exception as e:
                print(f"Ошибка RSS {feed['url']}: {e}")
        await asyncio.sleep(60)

def get_send_interval_from_db():
    conn = sqlite3.connect('rss.db')
    c = conn.cursor()
    c.execute("SELECT interval FROM rss_feeds LIMIT 1")
    row = c.fetchone()
    conn.close()
    if row:
        return row[0]  # значение из базы
    return 60  # дефолт

# ====================== Изменённая пост-новости ======================
async def post_news():
    while True:
        if news_queue:
            entry = news_queue.pop(0)
            text = f"<b>{entry.title}</b>\n{entry.link}"
            try:
                await bot.send_message(CHANNEL_ID, text)
            except Exception as e:
                print(f"Ошибка отправки: {e}")
        interval = get_send_interval_from_db()  # берём из sqlite
        await asyncio.sleep(interval * SEND_INTERVAL)

async def main():
    asyncio.create_task(fetch_feeds())
    asyncio.create_task(post_news())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())