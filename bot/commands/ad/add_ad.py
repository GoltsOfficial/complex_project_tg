from aiogram.types import Message
from bot.db.database import add_ad

async def add_ad_handler(message: Message, user_states):
    chat_id = message.chat.id
    state = user_states[chat_id]
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
            del user_states[chat_id]
        except:
            await message.answer("❌ Введите число.")
