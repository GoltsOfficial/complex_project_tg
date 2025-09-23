from aiogram.types import Message
from bot.db.database import add_feed

async def add_rss_handler(message: Message, user_states):
    chat_id = message.chat.id
    state = user_states[chat_id]
    text = message.text.strip()

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
