# run_bots.py (в корне проекта)
import asyncio
import logging
import os
import sys

# Добавляем пути для импортов
sys.path.append(os.path.dirname(__file__))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    logger.info("Запуск ботов...")
    
    try:
        # Импортируем и инициализируем ad_bot
        from ad_bot.models import init_db as init_ad_db
        from ad_bot.loader import dp as ad_dp, bot as ad_bot
        import ad_bot.handlers  # регистрируем хэндлеры
        
        init_ad_db()
        logger.info("Ad bot инициализирован")
    except Exception as e:
        logger.error(f"Ошибка инициализации ad_bot: {e}")
        return

    try:
        # Импортируем и инициализируем news_bot
        from news_bot.db.database import init_db as init_news_db
        from news_bot.main import dp as news_dp, bot as news_bot, fetch_feeds, post_ads
        
        init_news_db()
        logger.info("News bot инициализирован")
    except Exception as e:
        logger.error(f"Ошибка инициализации news_bot: {e}")
        return

    # Запускаем фоновые задачи для news_bot
    background_tasks = []
    try:
        background_tasks.append(asyncio.create_task(fetch_feeds()))
        background_tasks.append(asyncio.create_task(post_ads()))
        logger.info("Фоновые задачи news_bot запущены")
    except Exception as e:
        logger.warning(f"Не удалось запустить фоновые задачи: {e}")

    # Запускаем polling для обоих ботов
    logger.info("Старт polling для обоих ботов...")
    
    tasks = [
        asyncio.create_task(news_dp.start_polling(news_bot, skip_updates=True)),
        asyncio.create_task(ad_dp.start_polling(ad_bot, skip_updates=True))
    ]

    try:
        await asyncio.gather(*tasks)
    except Exception as e:
        logger.error(f"Ошибка в работе ботов: {e}")
    finally:
        # Отменяем все задачи при завершении
        for task in tasks + background_tasks:
            task.cancel()
        
        # Ждем завершения всех задач
        await asyncio.gather(*tasks, *background_tasks, return_exceptions=True)
        
        # Закрываем сессии ботов
        await ad_bot.session.close()
        await news_bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
