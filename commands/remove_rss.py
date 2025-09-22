# commands/remove_rss.py
from aiogram.types import Message

async def remove_rss_handler(message: Message, rss_feeds, user_states):
    chat_id = message.chat.id
    text = message.text.strip()

    if chat_id not in user_states:
        if not rss_feeds:
            await message.answer("Список RSS пуст.")
            return
        user_states[chat_id] = {"mode": "remove", "step": 0}
        msg = "📃 Выберите номер RSS для удаления:\n" + \
              "\n".join(f"{i+1}. {rss['name']} ({rss['url']})" for i, rss in enumerate(rss_feeds))
        await message.answer(msg)
        return

    state = user_states[chat_id]
    try:
        index = int(text) - 1
        if 0 <= index < len(rss_feeds):
            removed = rss_feeds.pop(index)
            del user_states[chat_id]
            await message.answer(f"🗑 RSS удалён: {removed['name']}")
        else:
            await message.answer("❌ Неверный номер.")
    except:
        await message.answer("❌ Введите число.")
