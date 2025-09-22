# commands/add_rss.py
from aiogram.types import Message

async def add_rss_handler(message: Message, rss_feeds, user_states):
    chat_id = message.chat.id
    text = message.text.strip()

    # если пришла команда /add_rss — начинаем интерактив
    if text == "/add_rss":
        user_states[chat_id] = {"mode": "add", "step": 0, "data": {}}
        await message.answer("🔗 Введите ссылку на RSS:")
        return

    # если пользователь в интерактиве "add"
    if chat_id in user_states and user_states[chat_id].get("mode") == "add":
        state = user_states[chat_id]
        step = state["step"]

        if step == 0:
            state["data"]["url"] = text
            state["step"] = 1
            await message.answer("📝 Введите название RSS:")
        elif step == 1:
            state["data"]["name"] = text
            state["step"] = 2
            await message.answer("⏱ Введите интервал в минутах:")
        elif step == 2:
            try:
                interval = int(message.text.strip())
                state["data"]["interval"] = interval * 60  # сохраняем в секундах
                rss_feeds.append(state["data"])
                del user_states[chat_id]
                await message.answer(f"✅ RSS добавлен: {state['data']['name']}")
            except ValueError:
                await message.answer("❌ Введите число интервала в минутах.")
        return

    # любая другая команда — прерываем интерактив
    if text.startswith("/"):
        if chat_id in user_states:
            del user_states[chat_id]
