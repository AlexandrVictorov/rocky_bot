import asyncio
from aiogram import Bot
from aiogram import Dispatcher

from config import TOKEN
from middlewares import LoggingMiddleware
from heandlers import setup_heandlers

bot = Bot(token=TOKEN)
dp = Dispatcher() # Dispatcher управляет обработчиками событий.

dp.message.middleware(LoggingMiddleware()) # подключаем логирование сообщений пользователя

async def main():
    await setup_heandlers(dp) # вызываем функцию подключения роутеров
    print("Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())