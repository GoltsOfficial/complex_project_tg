import logging
import sys
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

# ⚡ Токен берем из main.py
from ad_bot.main import AD_BOT_TOKEN

logging.basicConfig(level=logging.INFO, stream=sys.stdout)

bot: Bot = Bot(
    token=AD_BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp: Dispatcher = Dispatcher()