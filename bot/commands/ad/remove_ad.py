from aiogram.types import Message
from bot.db.database import decrement_ad_view

async def remove_ad_handler(message: Message):
    text = message.text.strip()
    try:
        ad_id = int(text)
        decrement_ad_view(ad_id)
        await message.answer(f"✅ Реклама удалена/уменьшена.")
    except:
        await message.answer("❌ Неверный ID.")
