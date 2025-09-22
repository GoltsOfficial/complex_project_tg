from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

async def edit_rss_handler(message: types.Message, rss_feeds, user_states):
    chat_id = message.chat.id
    text = message.text.strip()

    # Начало интерактива
    if chat_id not in user_states or user_states[chat_id].get("mode") != "edit":
        if not rss_feeds:
            await message.answer("Список RSS пуст.")
            return

        # Выводим список RSS с нумерацией с 1
        text_list = "📃 Выберите номер RSS для редактирования:\n" + \
                    "\n".join(f"{i+1}. {rss['name']} ({rss['url']})" for i, rss in enumerate(rss_feeds))
        await message.answer(text_list)
        user_states[chat_id] = {"mode": "edit", "step": 0}
        return

    state = user_states[chat_id]
    step = state["step"]

    if step == 0:
        try:
            # очищаем текст
            text_clean = text.strip()
            num = int(text_clean)  # пользователь вводит номер с 1
            if 1 <= num <= len(rss_feeds):
                index = num - 1
                state["index"] = index
                state["step"] = 1

                # Кнопки выбора поля
                keyboard = InlineKeyboardMarkup(row_width=1)
                keyboard.add(
                    InlineKeyboardButton("Ссылка", callback_data="edit_url"),
                    InlineKeyboardButton("Название", callback_data="edit_name"),
                    InlineKeyboardButton("Интервал", callback_data="edit_interval")
                )
                await message.answer(f"Вы выбрали #{num}: {rss_feeds[index]['name']}\nВыберите, что изменить:",
                                     reply_markup=keyboard)
            else:
                await message.answer(f"❌ Неверный номер. Введите число от 1 до {len(rss_feeds)}")
        except Exception:
            await message.answer("❌ Введите корректное число.")
