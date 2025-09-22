from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

async def edit_rss_handler(message: types.Message, rss_feeds, user_states):
    chat_id = message.chat.id
    text = message.text.strip()

    if chat_id not in user_states:
        if not rss_feeds:
            await message.answer("Список RSS пуст.")
            return

        user_states[chat_id] = {"mode": "edit", "step": 0}
        msg = "📃 Выберите номер RSS для редактирования:\n" + \
              "\n".join(f"{i+1}. {rss['name']} ({rss['url']})" for i, rss in enumerate(rss_feeds))
        await message.answer(msg)
        return

    state = user_states[chat_id]
    step = state["step"]

    # Шаг 0 — ввод номера
    if step == 0:
        try:
            num = int(text)
            if 1 <= num <= len(rss_feeds):
                index = num - 1
                state["index"] = index
                state["step"] = 1

                keyboard = InlineKeyboardMarkup(row_width=1)
                keyboard.add(
                    InlineKeyboardButton("Ссылка", callback_data="edit_url"),
                    InlineKeyboardButton("Название", callback_data="edit_name"),
                    InlineKeyboardButton("Интервал", callback_data="edit_interval")
                )
                await message.answer(
                    f"Вы выбрали #{num}: {rss_feeds[index]['name']}\nВыберите, что изменить:",
                    reply_markup=keyboard
                )
            else:
                await message.answer(f"❌ Неверный номер. Введите число от 1 до {len(rss_feeds)}")
        except ValueError:
            await message.answer("❌ Введите корректное число.")
