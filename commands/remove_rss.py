from aiogram.types import Message


async def remove_rss_handler(message: Message, rss_feeds, user_states):
    chat_id = message.chat.id
    text = message.text.strip()
    state = user_states.get(chat_id, {})

    # Если это первый шаг (показ списка)
    if state.get("step") == 0:
        if not rss_feeds:
            await message.answer("📭 Список RSS пуст.")
            if chat_id in user_states:
                del user_states[chat_id]
            return

        # Показываем список RSS
        msg = "📃 Выберите номер RSS для удаления:\n\n" + \
              "\n".join(f"{i + 1}. {rss['name']} ({rss['url']})" for i, rss in enumerate(rss_feeds))

        state["step"] = 1
        state["rss_list"] = rss_feeds.copy()  # Сохраняем копию списка
        user_states[chat_id] = state  # Обновляем состояние
        await message.answer(msg)

    # Если это второй шаг (обработка выбора номера)
    elif state.get("step") == 1:
        try:
            index = int(text) - 1  # Преобразуем в индекс (0-based)

            # Проверяем валидность индекса
            if 0 <= index < len(rss_feeds):
                # Удаляем RSS
                removed_rss = rss_feeds.pop(index)
                await message.answer(f"✅ RSS удален: {removed_rss['name']}")

                # Очищаем состояние
                del user_states[chat_id]
            else:
                await message.answer(f"❌ Неверный номер. Введите число от 1 до {len(rss_feeds)}:")

        except ValueError:
            await message.answer("❌ Пожалуйста, введите число:")