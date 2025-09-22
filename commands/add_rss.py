from aiogram.types import Message


async def add_rss_handler(message: Message, rss_feeds, user_states):
    chat_id = message.chat.id
    text = message.text.strip()
    state = user_states[chat_id]

    if state["step"] == 0:
        # Шаг 1: Получаем URL
        state["url"] = text
        state["step"] = 1
        await message.answer("📝 Введите название для RSS:")

    elif state["step"] == 1:
        # Шаг 2: Получаем название
        state["name"] = text
        state["step"] = 2
        await message.answer("⏱ Введите интервал обновления в минутах:")

    elif state["step"] == 2:
        # Шаг 3: Получаем интервал
        try:
            interval = int(text)
            if interval <= 0:
                await message.answer("❌ Интервал должен быть положительным числом. Попробуйте снова:")
                return

            # Сохраняем RSS
            rss_data = {
                "name": state["name"],
                "url": state["url"],
                "interval": interval
            }
            rss_feeds.append(rss_data)

            await message.answer(
                f"✅ RSS добавлен!\nНазвание: {state['name']}\nURL: {state['url']}\nИнтервал: {interval} мин.")
            del user_states[chat_id]  # Завершаем интерактив

        except ValueError:
            await message.answer("❌ Введите число для интервала:")