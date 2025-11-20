import asyncio
import logging
import os
import sys
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def main():
    try:
        # Импортируем handlers
        from handlers import user_handlers, admin_handlers
        
        # Регистрация роутеров
        user_handlers.register_handlers(dp)
        admin_handlers.register_handlers(dp)
        
        print("🤖 Бот 'Приватка Фазиля' запущен на Render!")
        print("📍 Для остановки нужно удалить сервис в панели Render")
        
        await dp.start_polling()
        
    except Exception as e:
        print(f"💥 Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Проверяем переменные окружения
    from config import BOT_TOKEN
    
    if not BOT_TOKEN or BOT_TOKEN == "your_bot_token_here":
        print("❌ Ошибка: BOT_TOKEN не установлен!")
        print("💡 Установите BOT_TOKEN в настройках Render")
        sys.exit(1)
    
    # Инициализация бота и диспетчера для aiogram 2.x
    bot = Bot(token=BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(bot, storage=storage)
    
    # Запуск бота
    asyncio.run(main())