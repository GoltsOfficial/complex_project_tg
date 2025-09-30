# ad_bot/config.py
import os

TOKEN = os.getenv("AD_BOT_TOKEN")  # обязательна
PROVIDER_TOKEN = os.getenv("AD_PROVIDER_TOKEN", "")  # провайдер (может быть тестовый)
CURRENCY = os.getenv("AD_CURRENCY", "RUB")
PRICE_PER_MONTH_RUB = int(os.getenv("AD_PRICE_PER_MONTH_RUB", "500"))
DATABASE_PATH = os.getenv("AD_DATABASE_PATH", "payments.db")
