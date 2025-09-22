from aiogram.types import Message
from bot.db.database import update_feed, get_all_feeds

async def handle_edit_rss_input(message: Message, user_states):
    chat_id = message.chat.id
    text = message.text.strip()
    state = user_states.get(chat_id)
    if not state or state.get("step") != 3:
        return False

    feed_id = state["feed_id"]
    field = state["editing_field"]
    value = int(text) if field == "interval" else text

    update_feed(feed_id, field, value)
    feed = next(f for f in get_all_feeds() if f['id'] == feed_id)
    await message.answer(f"✅ {field} изменено! Текущее значение: {feed[field]}")
    del user_states[chat_id]
    return True
