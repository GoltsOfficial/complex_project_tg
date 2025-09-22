from aiogram.types import CallbackQuery
from bot.db.database import update_feed

async def edit_rss_callback_handler(callback_query: CallbackQuery, user_states):
    chat_id = callback_query.from_user.id
    state = user_states.get(chat_id)
    data = callback_query.data

    if not state:
        await callback_query.answer("❌ Сессия истекла.")
        return

    state["editing_field"] = {
        "edit_name": "name",
        "edit_url": "url",
        "edit_interval": "interval"
    }.get(data)

    if state["editing_field"]:
        state["step"] = 3
        await callback_query.message.answer(f"Введите новое значение для {state['editing_field']}:")

    await callback_query.answer()
