import subprocess
import os
from dotenv import load_dotenv
import logging
import time

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

def run_bot():
    logging.info("Запуск Telegram-бота...")
    process = subprocess.Popen(
        ["/home/alert/cardolero_lalala_bot/venv/bin/python", "-m", "bot.main"],
        stdout=open('bot.log', 'a'),
        stderr=open('bot_err.log', 'a'),
        text=True
    )
    logging.info(f"Бот запущен с PID: {process.pid}")
    process.wait()

def run_flask():
    logging.info("Запуск Flask-админки...")
    load_dotenv()
    process = subprocess.Popen(
        ["/home/alert/cardolero_lalala_bot/venv/bin/gunicorn", "-w", "4", "-b", "0.0.0.0:9090", "web.app:app"],
        stdout=open('flask.log', 'a'),
        stderr=open('flask_err.log', 'a'),
        text=True
    )
    logging.info(f"Flask запущен с PID: {process.pid}")
    process.wait()

if __name__ == "__main__":
    logging.info("Запуск процессов...")
    bot_process = subprocess.Popen(
        ["/home/alert/cardolero_lalala_bot/venv/bin/python", "-m", "bot.main"],
        stdout=open('bot.log', 'a'),
        stderr=open('bot_err.log', 'a'),
        text=True
    )
    flask_process = subprocess.Popen(
        ["/home/alert/cardolero_lalala_bot/venv/bin/gunicorn", "-w", "4", "-b", "0.0.0.0:9090", "web.app:app"],
        stdout=open('flask.log', 'a'),
        stderr=open('flask_err.log', 'a'),
        text=True
    )
    logging.info(f"Бот PID: {bot_process.pid}, Flask PID: {flask_process.pid}")
    try:
        while True:
            time.sleep(1)  # Держим главный процесс активным
    except KeyboardInterrupt:
        logging.info("Завершение процессов...")
        bot_process.terminate()
        flask_process.terminate()
        bot_process.wait()
        flask_process.wait()
        logging.info("Все процессы завершены.")