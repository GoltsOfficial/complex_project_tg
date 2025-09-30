import subprocess
import sys
import time
import signal

print("🚀 Запускаю ботов...")

processes = []

print("🤖 Запускаю News Bot...")
news_process = subprocess.Popen([sys.executable, "news_bot/main.py"])
processes.append(news_process)

time.sleep(3)

print("🤖 Запускаю Ad Bot...")
ad_process = subprocess.Popen([sys.executable, "ad_bot/main.py"])
processes.append(ad_process)

print("🎉 Все боты запущены!")

def signal_handler(sig, frame):
    print("\n🛑 Останавливаю ботов...")
    for process in processes:
        process.terminate()
    for process in processes:
        process.wait()
    print("✅ Все боты остановлены")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

try:
    while True:
        for i, process in enumerate(processes):
            if process.poll() is not None:
                print(f"⚠️ Процесс {i+1} неожиданно завершился")
        time.sleep(5)
except KeyboardInterrupt:
    signal_handler(None, None)