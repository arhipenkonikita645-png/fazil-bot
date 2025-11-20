import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

async def main():
    # Импортируем handlers здесь чтобы избежать циклических импортов
    from handlers import user_handlers, admin_handlers
    
    # Регистрация роутеров
    dp.include_router(user_handlers.router)
    dp.include_router(admin_handlers.router)
    
    print("Бот 'Приватка Фазиля' запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())