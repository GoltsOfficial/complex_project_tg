# run_bots.py (в корне проекта)
import asyncio
import logging
import os

# импортируем пакеты — при импорте хэндлеры зарегистрируются
import ad_bot.handlers as _ad_handlers  # noqa: F401 — регистрирует хэндлеры
from ad_bot.models import init_db as init_ad_db

import news_bot.main as news_main  # содержит bot, dp, фоновые задачи и registered handlers
# news_main уже регистрирует handlers при импорте

# убедимся, что news_bot.db.init / ad_bot init если нужно
try:
    # news_bot.db.database.init_db() уже вызывается при импорте модуля news_bot.db.database
    pass
except Exception:
    pass

async def main():
    logging.info("Инициализация баз данных...")
    try:
        init_ad_db()
    except Exception as e:
        logging.warning("Не удалось явно инициализировать ad_bot DB: %s", e)

    # запустим фоновые таски для news_bot
    try:
        asyncio.create_task(news_main.fetch_feeds())
        asyncio.create_task(news_main.post_ads())
    except Exception as e:
        logging.warning("Не удалось запустить фоновые задачи news_bot: %s", e)

    logging.info("Старт polling для обоих ботов...")
    tasks = [
        asyncio.create_task(news_main.dp.start_polling(news_main.bot, skip_updates=False)),
        asyncio.create_task(_ad_handlers.dp.start_polling(_ad_handlers.bot, skip_updates=False))
    ]

    await asyncio.gather(*tasks)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
