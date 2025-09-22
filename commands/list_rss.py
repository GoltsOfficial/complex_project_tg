# commands/list_rss.py
from aiogram.types import Message

async def list_rss_handler(message: Message, rss_feeds):
    if not rss_feeds:
        await message.answer("📭 Список RSS пуст.")
        return
    text = "📃 Текущие RSS-ленты:\n" + "\n".join(
        f"{i+1}. {rss['name']} ({rss['url']})" for i, rss in enumerate(rss_feeds)
    )
    await message.answer(text)
