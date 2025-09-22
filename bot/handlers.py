from aiogram import types
from bot.db.database import get_all_feeds, add_feed, update_feed, delete_feed, get_all_ads, add_ad, decrement_ad_view
from bot.states import user_states
from datetime import datetime

async def handle_message(message: types.Message):
    chat_id = message.chat.id
    text = message.text.strip()

    if chat_id in user_states:
        await handle_user_state(message)
        return

    if text == "/start":
        await message.answer(
            "🤖 RSS Bot\nКоманды:\n"
            "/add_rss /list_rss /edit_rss /remove_rss\n"
            "Реклама:\n/add_ad /list_ads /remove_ad"
        )
    elif text == "/add_rss":
        user_states[chat_id] = {"mode": "add", "step": 1}
        await message.answer("🔗 Введите ссылку RSS:")
    elif text == "/list_rss":
        feeds = get_all_feeds()
        if not feeds:
            await message.answer("📭 Список RSS пуст.")
            return
        await message.answer(
            "📃 RSS ленты:\n" +
            "\n".join(f"ID: {f['id']} | {f['name']} | {f['interval']}мин" for f in feeds)
        )
    elif text == "/edit_rss":
        feeds = get_all_feeds()
        if not feeds:
            await message.answer("📭 Список RSS пуст.")
            return
        user_states[chat_id] = {"mode": "edit", "step": 1}
        await message.answer(
            "📃 Выберите ID RSS:\n" +
            "\n".join(f"ID: {f['id']} - {f['name']}" for f in feeds)
        )
    elif text == "/remove_rss":
        feeds = get_all_feeds()
        if not feeds:
            await message.answer("📭 Список RSS пуст.")
            return
        user_states[chat_id] = {"mode": "remove", "step": 1}
        await message.answer(
            "🗑 Выберите ID RSS для удаления:\n" +
            "\n".join(f"ID: {f['id']} - {f['name']}" for f in feeds)
        )
    elif text == "/add_ad":
        user_states[chat_id] = {"mode": "add_ad", "step": 1}
        await message.answer("📝 Введите текст рекламы:")
    elif text == "/list_ads":
        ads = get_all_ads()
        if not ads:
            await message.answer("📭 Реклам пуст.")
            return
        await message.answer(
            "📢 Рекламные записи:\n" +
            "\n".join(f"ID: {a['id']} | {a['text']} | Осталось показов: {a['views']}" for a in ads)
        )
    elif text == "/remove_ad":
        ads = get_all_ads()
        if not ads:
            await message.answer("📭 Реклам пуст.")
            return
        user_states[chat_id] = {"mode": "remove_ad", "step": 1}
        await message.answer(
            "🗑 Выберите ID рекламы для удаления:\n" +
            "\n".join(f"ID: {a['id']} - {a['text']}" for a in ads)
        )
    else:
        await message.answer("❌ Неверная команда.")

async def handle_user_state(message: types.Message):
    chat_id = message.chat.id
    text = message.text.strip()
    state = user_states[chat_id]

    if text.startswith("/"):
        del user_states[chat_id]
        return

    # ===== RSS Add/Edit/Delete =====
    if state["mode"] == "add":
        if state["step"] == 1:
            state["url"] = text
            state["step"] = 2
            await message.answer("📝 Введите название RSS:")
        elif state["step"] == 2:
            state["name"] = text
            state["step"] = 3
            await message.answer("⏱ Интервал в минутах:")
        elif state["step"] == 3:
            try:
                interval = int(text)
                add_feed(state["name"], state["url"], interval)
                await message.answer(f"✅ RSS добавлен!")
                del user_states[chat_id]
            except:
                await message.answer("❌ Введите число.")

    elif state["mode"] == "remove":
        if state["step"] == 1:
            try:
                feed_id = int(text)
                delete_feed(feed_id)
                await message.answer(f"✅ RSS удален!")
                del user_states[chat_id]
            except:
                await message.answer("❌ Неверный ID.")

    # ===== Ads Add/Delete =====
    elif state["mode"] == "add_ad":
        if state["step"] == 1:
            state["text"] = text
            state["step"] = 2
            await message.answer("Введите количество показов:")
        elif state["step"] == 2:
            try:
                views = int(text)
                add_ad(state["text"], views)
                await message.answer(f"✅ Реклама добавлена! Показов: {views}")
                del user_states[chat_id]
            except:
                await message.answer("❌ Введите число.")

    elif state["mode"] == "remove_ad":
        if state["step"] == 1:
            try:
                ad_id = int(text)
                decrement_ad_view(ad_id)  # удалит если views <= 0
                await message.answer(f"✅ Реклама удалена/уменьшена.")
                del user_states[chat_id]
            except:
                await message.answer("❌ Неверный ID.")
