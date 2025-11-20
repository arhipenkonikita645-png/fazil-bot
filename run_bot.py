import asyncio
import logging
import sys

# Настройка подробного логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def main():
    print("🚀 Запуск бота 'Приватка Фазиля'...")
    
    try:
        from bot import main as bot_main
        print("✅ Все модули загружены успешно")
        print("🤖 Бот запускается...")
        
        await bot_main()
        
    except KeyboardInterrupt:
        print("\n🛑 Бот остановлен пользователем")
    except Exception as e:
        print(f"💥 Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
        input("Нажмите Enter для выхода...")

if __name__ == "__main__":
    # Добавляем обработчик для корректного завершения
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 До свидания!")
    except Exception as e:
        print(f"💥 Необработанная ошибка: {e}")
        input("Нажмите Enter для выхода...")