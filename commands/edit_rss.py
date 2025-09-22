from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

async def edit_rss_handler(message: types.Message, rss_feeds, user_states):
    chat_id = message.chat.id
    text = message.text.strip()

    # Если интерактив ещё не начался — выводим список RSS
    if chat_id not in user_states or user_states[chat_id].get("mode") != "edit":
        if not rss_feeds:
            await message.answer("Список RSS пуст.")
            return

        msg = "📃 Выберите номер RSS для редактирования:\n" + \
              "\n".join(f"{i+1}. {rss['name']} ({rss['url']})" for i, rss in enumerate(rss_feeds))
        await message.answer(msg)
        user_states[chat_id] = {"mode": "edit", "step": 0}
        return

    state = user_states[chat_id]
    step = state["step"]

    # Шаг 0 — ввод номера RSS
    if step == 0:
        try:
            num = int(text)
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
        except:
            await message.answer("❌ Введите корректное число.")

# Callback handler для кнопок
async def edit_rss_callback_handler(callback: types.CallbackQuery, rss_feeds, user_states):
    chat_id = callback.from_user.id
    if chat_id not in user_states or user_states[chat_id].get("mode") != "edit":
        await callback.answer("❌ Сначала выберите RSS через /edit_rss")
        return

    state = user_states[chat_id]
    index = state["index"]

    if callback.data in ["edit_url", "edit_name", "edit_interval"]:
        state["field"] = callback.data.split("_")[1]
        state["step"] = 2
        await callback.message.answer(f"Введите новое значение для {rss_feeds[index]['name']}:")
        await callback.answer()

# Шаг 2 — применение нового значения
async def edit_rss_apply_handler(message: types.Message, rss_feeds, user_states):
    chat_id = message.chat.id
    if chat_id not in user_states or user_states[chat_id].get("mode") != "edit":
        return

    state = user_states[chat_id]
    index = state["index"]
    field = state.get("field")
    text = message.text.strip()

    if field == "interval":
        try:
            interval = int(text)
            rss_feeds[index]["interval"] = interval * 60
        except:
            await message.answer("❌ Введите число интервала.")
            return
    else:
        rss_feeds[index][field] = text

    await message.answer(f"✅ RSS обновлён: {rss_feeds[index]['name']}")
    del user_states[chat_id]
