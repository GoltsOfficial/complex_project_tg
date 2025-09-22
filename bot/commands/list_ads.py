from aiogram.types import Message
from bot.db.database import get_all_ads

async def list_ads_handler(message: Message):
    ads = get_all_ads()
    if not ads:
        await message.answer("📭 Реклам пуст.")
        return
    await message.answer(
        "📢 Рекламные записи:\n" +
        "\n".join(f"ID: {a['id']} | {a['text']} | Осталось показов: {a['views']}" for a in ads)
    )
