from aiogram import BaseMiddleware
from aiogram.types import Message

class LoggingMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Message, data: dict):
        print(f"Получено сообщение {event.text}") # логируем запросы в консоль и вызываем нужный обработчик
        return await handler(event, data)
              