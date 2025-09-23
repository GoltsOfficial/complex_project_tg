from aiogram.types import Message
from bot.db.database import delete_feed

async def remove_rss_handler(message: Message, user_states):
    chat_id = message.chat.id
    state = user_states[chat_id]
    text = message.text.strip()

    if state["step"] == 1:
        try:
            feed_id = int(text)
            delete_feed(feed_id)
            await message.answer(f"✅ RSS удален!")
            del user_states[chat_id]
        except:
            await message.answer("❌ Неверный ID.")
