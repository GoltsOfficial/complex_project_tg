from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from bot.db.database import get_all_feeds, update_feed

async def edit_rss_handler(message: Message, user_states):
    chat_id = message.chat.id
    state = user_states[chat_id]
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
            await message.answer(
                f"Выбран RSS: {feed['name']}\nЧто хотите изменить?",
                reply_markup=keyboard
            )
        except:
            await message.answer("❌ Введите число ID.")
