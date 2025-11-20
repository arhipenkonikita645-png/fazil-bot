import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

# Настройка логирования
logging.basicConfig(level=logging.INFO)

async def main():
    try:
        # Импортируем handlers здесь чтобы избежать циклических импортов
        from handlers import user_handlers, admin_handlers
        
        # Регистрация роутеров
        dp.include_router(user_handlers.router)
        dp.include_router(admin_handlers.router)
        
        print("🤖 Бот 'Приватка Фазиля' запущен!")
        await dp.start_polling(bot)
        
    except Exception as e:
        print(f"💥 Ошибка: {e}")

if __name__ == "__main__":
    # Инициализация бота и диспетчера
    from config import BOT_TOKEN
    
    bot = Bot(token=BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    # Запуск бота
    asyncio.run(main())
