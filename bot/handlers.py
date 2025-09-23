# bot/handlers.py
from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot.db.database import (
    add_feed, get_all_feeds, update_feed, delete_feed,
    add_ad, get_all_ads, update_ad, decrement_ad_view
)
from bot.states import user_states

# ====================== Основной обработчик сообщений ======================
async def handle_message(message: types.Message):
    chat_id = message.chat.id
    text = message.text.strip()

    # Если пользователь находится в интерактивном режиме
    if chat_id in user_states:
        state = user_states[chat_id]

        # ===== RSS =====
        if state["mode"] == "add_rss":
            await handle_add_rss(message, state)
            return
        elif state["mode"] == "edit_rss":
            await handle_edit_rss(message, state)
            return
        elif state["mode"] == "remove_rss":
            await handle_remove_rss(message, state)
            return

        # ===== Ads =====
        elif state["mode"] == "add_ad":
            await handle_add_ad(message, state)
            return
        elif state["mode"] == "edit_ad":
            await handle_edit_ad(message, state)
            return
        elif state["mode"] == "remove_ad":
            await handle_remove_ad(message, state)
            return

    # Основные команды
    if text == "/start":
        await message.answer(
            "🤖 Меню бота\n\n"
            "RSS:\n"
            "/add_rss — добавить RSS\n"
            "/edit_rss — изменить RSS\n"
            "/remove_rss — удалить RSS\n"
            "/list_rss — список RSS\n\n"
            "Реклама:\n"
            "/add_ad — добавить рекламу\n"
            "/edit_ad — изменить рекламу\n"
            "/remove_ad — удалить рекламу\n"
            "/list_ads — список рекламы"
        )
    elif text == "/add_rss":
        user_states[chat_id] = {"mode": "add_rss", "step": 1}
        await message.answer("🔗 Введите ссылку RSS:")
    elif text == "/list_rss":
        feeds = get_all_feeds()
        if not feeds:
            await message.answer("📭 Список RSS пуст.")
            return
        msg = "📃 Текущие RSS-ленты:\n" + "\n".join(
            f"ID: {f['id']} | {f['name']} | Интервал: {f['interval']} мин" for f in feeds
        )
        await message.answer(msg)
    elif text == "/edit_rss":
        feeds = get_all_feeds()
        if not feeds:
            await message.answer("📭 Список RSS пуст.")
            return
        user_states[chat_id] = {"mode": "edit_rss", "step": 1}
        msg = "📃 Введите ID RSS для редактирования:\n" + "\n".join(
            f"{f['id']} - {f['name']}" for f in feeds
        )
        await message.answer(msg)
    elif text == "/remove_rss":
        feeds = get_all_feeds()
        if not feeds:
            await message.answer("📭 Список RSS пуст.")
            return
        user_states[chat_id] = {"mode": "remove_rss", "step": 1}
        msg = "🗑 Введите ID RSS для удаления:\n" + "\n".join(
            f"{f['id']} - {f['name']}" for f in feeds
        )
        await message.answer(msg)
    elif text == "/add_ad":
        user_states[chat_id] = {"mode": "add_ad", "step": 1}
        await message.answer("Введите текст рекламы:")
    elif text == "/edit_ad":
        ads = get_all_ads()
        if not ads:
            await message.answer("📭 Реклам пуст.")
            return
        user_states[chat_id] = {"mode": "edit_ad", "step": 1}
        msg = "Введите ID рекламы для редактирования:\n" + "\n".join(
            f"{a['id']} - {a['text']} (Осталось показов: {a['views']})" for a in ads
        )
        await message.answer(msg)
    elif text == "/remove_ad":
        ads = get_all_ads()
        if not ads:
            await message.answer("📭 Реклам пуст.")
            return
        user_states[chat_id] = {"mode": "remove_ad", "step": 1}
        msg = "Введите ID рекламы для удаления/уменьшения показов:\n" + "\n".join(
            f"{a['id']} - {a['text']} (Осталось показов: {a['views']})" for a in ads
        )
        await message.answer(msg)
    elif text == "/list_ads":
        ads = get_all_ads()
        if not ads:
            await message.answer("📭 Реклам пуст.")
            return
        msg = "📢 Список рекламы:\n" + "\n".join(
            f"ID: {a['id']} | {a['text']} | Осталось показов: {a['views']}" for a in ads
        )
        await message.answer(msg)
    else:
        await message.answer("❌ Неверная команда.")


# ====================== RSS ======================
async def handle_add_rss(message: types.Message, state):
    text = message.text.strip()
    if state["step"] == 1:
        state["url"] = text
        state["step"] = 2
        await message.answer("📝 Введите название RSS:")
    elif state["step"] == 2:
        state["name"] = text
        state["step"] = 3
        await message.answer("⏱ Введите интервал в минутах:")
    elif state["step"] == 3:
        try:
            interval = int(text)
            add_feed(state["name"], state["url"], interval)
            await message.answer("✅ RSS добавлен!")
            del user_states[message.chat.id]
        except:
            await message.answer("❌ Введите число.")


async def handle_edit_rss(message: types.Message, state):
    text = message.text.strip()
    if state["step"] == 1:
        try:
            feed_id = int(text)
            feed = next((f for f in get_all_feeds() if f['id'] == feed_id), None)
            if not feed:
                await message.answer("❌ Неверный ID.")
                return
            state["feed_id"] = feed_id
            state["step"] = 2
            keyboard = InlineKeyboardMarkup(row_width=3)
            keyboard.add(
                InlineKeyboardButton("✏️ Название", callback_data="edit_name"),
                InlineKeyboardButton("🔗 Ссылка", callback_data="edit_url"),
                InlineKeyboardButton("⏰ Интервал", callback_data="edit_interval")
            )
            await message.answer("Выберите что изменить:", reply_markup=keyboard)
        except:
            await message.answer("❌ Введите число ID.")
    elif state["step"] == 3:
        field = state.get("editing_field")
        value = int(text) if field == "interval" else text
        update_feed(state["feed_id"], field, value)
        await message.answer(f"✅ {field} обновлено!")
        del user_states[message.chat.id]


async def handle_remove_rss(message: types.Message, state):
    text = message.text.strip()
    if state["step"] == 1:
        try:
            feed_id = int(text)
            delete_feed(feed_id)
            await message.answer("✅ RSS удален!")
            del user_states[message.chat.id]
        except:
            await message.answer("❌ Неверный ID.")


# ====================== Ads ======================
async def handle_add_ad(message: types.Message, state):
    text = message.text.strip()
    if state["step"] == 1:
        state["text"] = text
        state["step"] = 2
        await message.answer("Введите количество показов:")
    elif state["step"] == 2:
        try:
            views = int(text)
            add_ad(state["text"], views)
            await message.answer(f"✅ Реклама добавлена! Показов: {views}")
            del user_states[message.chat.id]
        except:
            await message.answer("❌ Введите число.")


async def handle_edit_ad(message: types.Message, state):
    text = message.text.strip()
    if state["step"] == 2:
        try:
            ad_id = state["ad_id"]
            update_ad(ad_id, text)
            await message.answer("✅ Текст рекламы обновлен!")
            del user_states[message.chat.id]
        except:
            await message.answer("❌ Ошибка изменения.")


async def handle_remove_ad(message: types.Message, state):
    text = message.text.strip()
    if state["step"] == 1:
        try:
            ad_id = int(text)
            decrement_ad_view(ad_id)
            await message.answer("✅ Реклама удалена/уменьшена показов!")
            del user_states[message.chat.id]
        except:
            await message.answer("❌ Неверный ID.")
