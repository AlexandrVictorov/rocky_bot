from dotenv import load_dotenv
import os

# Файл для загрузки токенов
load_dotenv()
print(f"Текущая папка: {os.getcwd()}")
print(f"Файл .env существует: {os.path.exists('.env')}")

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    exit("Ошибка: переменная BOT_TOKEN не найдена в файле .env")

API_THEWEATHER = os.getenv("API_THEWEATHER")
if not API_THEWEATHER:
    exit("Ошибка: переменная API_THEWEATHER не найдена в файле .env")