# ad_bot/loader.py
import sys
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from .config import TOKEN  # относительный импорт

logging.basicConfig(level=logging.INFO, stream=sys.stdout)

bot: Bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp: Dispatcher = Dispatcher()

