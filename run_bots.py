# run_bots.py - Простой загрузчик
import subprocess
import sys
import time

print("🚀 Запускаю ботов...")

# Запускаем news_bot
print("🤖 Запускаю News Bot...")
news_process = subprocess.Popen([sys.executable, "news_bot/main.py"])

# Ждем немного перед запуском второго бота
time.sleep(3)

# Запускаем ad_bot
print("🤖 Запускаю Ad Bot...")  
ad_process = subprocess.Popen([sys.executable, "ad_bot/main.py"])

print("🎉 Все боты запущены!")

# Бесконечный цикл чтобы главный процесс не завершался
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("🛑 Останавливаю ботов...")
    news_process.terminate()
    ad_process.terminate()
