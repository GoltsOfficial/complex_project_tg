# main.py
import asyncio
import logging

from loader import dp, bot
import handlers  # регистрируем хэндлеры
from models import init_db

async def main():
    init_db()  # создаём таблицы, если нужно
    try:
        # skip_updates=False как в статье — важно для корректной обработки платежных апдейтов
        await dp.start_polling(bot, skip_updates=False)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
