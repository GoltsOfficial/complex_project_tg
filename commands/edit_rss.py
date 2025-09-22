from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import Bot


async def edit_rss_handler(message: Message, rss_feeds, user_states):
    chat_id = message.chat.id
    state = user_states[chat_id]

    if state["step"] == 0:
        # Показываем список RSS
        if not rss_feeds:
            await message.answer("📭 Список RSS пуст.")
            del user_states[chat_id]
            return

        # Формируем сообщение с нумерацией с 1 для удобства
        msg = "📃 Выберите номер RSS для редактирования:\n\n" + \
              "\n".join(f"{i + 1}. {rss['name']} ({rss['url']})" for i, rss in enumerate(rss_feeds))

        state["step"] = 1
        state["rss_list"] = rss_feeds.copy()
        await message.answer(msg)

    elif state["step"] == 1:
        # Обрабатываем выбор номера
        try:
            index = int(message.text) - 1  # Преобразуем в индекс (0-based)
            if 0 <= index < len(rss_feeds):
                state["step"] = 2
                state["selected_index"] = index
                state["selected_rss"] = rss_feeds[index]

                # Показываем кнопки выбора действия
                keyboard = InlineKeyboardMarkup(row_width=2)
                keyboard.add(
                    InlineKeyboardButton("✏️ Название", callback_data="edit_name"),
                    InlineKeyboardButton("🔗 Ссылка", callback_data="edit_url"),
                    InlineKeyboardButton("⏰ Интервал", callback_data="edit_interval"),
                    InlineKeyboardButton("❌ Удалить", callback_data="delete_rss")
                )

                rss = rss_feeds[index]
                await message.answer(
                    f"📋 Выбран RSS: {rss['name']}\n"
                    f"🔗 Ссылка: {rss['url']}\n"
                    f"⏰ Интервал: {rss.get('interval', 'Не указан')} мин.\n\n"
                    f"Что вы хотите изменить?",
                    reply_markup=keyboard
                )
            else:
                await message.answer(f"❌ Неверный номер. Введите число от 1 до {len(rss_feeds)}:")
        except ValueError:
            await message.answer("❌ Введите число:")


async def edit_rss_callback_handler(callback_query: CallbackQuery, rss_feeds, user_states, bot: Bot):
    chat_id = callback_query.from_user.id
    data = callback_query.data

    if chat_id not in user_states:
        await callback_query.answer("❌ Сессия истекла.")
        return

    state = user_states[chat_id]

    if data == "edit_name":
        state["step"] = 3
        state["editing_field"] = "name"
        await callback_query.message.answer("✏️ Введите новое название:")

    elif data == "edit_url":
        state["step"] = 3
        state["editing_field"] = "url"
        await callback_query.message.answer("🔗 Введите новую ссылку:")

    elif data == "edit_interval":
        state["step"] = 3
        state["editing_field"] = "interval"
        await callback_query.message.answer("⏰ Введите новый интервал (в минутах):")

    elif data == "delete_rss":
        index = state["selected_index"]
        if 0 <= index < len(rss_feeds):
            removed_rss = rss_feeds.pop(index)
            await callback_query.message.answer(f"✅ RSS '{removed_rss['name']}' удален!")
            del user_states[chat_id]

    await callback_query.answer()


# Дополнительный хендлер для обработки ввода новых значений
async def handle_edit_input(message: Message, user_states, rss_feeds):
    chat_id = message.chat.id

    if chat_id not in user_states:
        return False

    state = user_states[chat_id]

    if state.get("step") == 3:  # Редактирование поля
        field = state.get("editing_field")
        index = state.get("selected_index")
        text = message.text.strip()

        if field and index is not None and 0 <= index < len(rss_feeds):
            if field == "interval":
                try:
                    value = int(text)
                    if value <= 0:
                        await message.answer("❌ Интервал должен быть положительным числом.")
                        return True
                except ValueError:
                    await message.answer("❌ Введите число для интервала.")
                    return True
            else:
                value = text

            # Сохраняем изменения
            old_value = rss_feeds[index].get(field, "Не указан")
            rss_feeds[index][field] = value

            await message.answer(f"✅ {field} изменен с '{old_value}' на '{value}'")
            del user_states[chat_id]
            return True

    return False