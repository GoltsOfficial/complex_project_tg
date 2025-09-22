from aiogram.types import Message
from bot.db.database import get_all_ads, update_ad

async def edit_ad_handler(message: Message, user_states):
    chat_id = message.chat.id
    state = user_states[chat_id]
    text = message.text.strip()

    if state["step"] == 1:
        try:
            ad_id = int(text)
            ad = next((a for a in get_all_ads() if a['id'] == ad_id), None)
            if not ad:
                await message.answer("❌ Неверный ID рекламы.")
                return

            state["ad_id"] = ad_id
            state["step"] = 2

            await message.answer("Введите новый текст рекламы:")
        except:
            await message.answer("❌ Введите число ID.")
    elif state["step"] == 2:
        ad_id = state["ad_id"]
        update_ad(ad_id, text)
        await message.answer(f"✅ Текст рекламы обновлен!")
        del user_states[chat_id]
