import sys
import traceback
import os

def test_imports():
    print("🔍 Тестируем импорты...")
    
    try:
        print("1. Проверяем aiogram...")
        from aiogram import Bot, Dispatcher
        from aiogram.fsm.storage.memory import MemoryStorage
        print("   ✅ aiogram OK")
    except Exception as e:
        print(f"   ❌ aiogram ошибка: {e}")
        return False

    try:
        print("2. Проверяем config...")
        from config import BOT_TOKEN, ADMIN_IDS
        print(f"   ✅ config OK, токен: {'установлен' if BOT_TOKEN and BOT_TOKEN != 'your_bot_token_here' else 'НЕ установлен'}")
    except Exception as e:
        print(f"   ❌ config ошибка: {e}")
        return False

    try:
        print("3. Проверяем database...")
        from database import Database
        db = Database()
        print("   ✅ database OK")
    except Exception as e:
        print(f"   ❌ database ошибка: {e}")
        traceback.print_exc()
        return False

    try:
        print("4. Проверяем handlers...")
        from handlers.user_handlers import router as user_router
        from handlers.admin_handlers import router as admin_router
        print("   ✅ handlers OK")
    except Exception as e:
        print(f"   ❌ handlers ошибка: {e}")
        traceback.print_exc()
        return False

    return True

def main():
    print("🚀 Запуск диагностики...")
    
    # Добавляем текущую директорию в путь
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, current_dir)
    
    print(f"📁 Рабочая директория: {current_dir}")
    print(f"🐍 Python версия: {sys.version}")
    
    # Проверяем файлы
    required_files = ['bot.py', 'database.py', 'config.py', 'keyboards.py', 
                     'handlers/__init__.py', 'handlers/user_handlers.py', 'handlers/admin_handlers.py', '.env']
    
    print("\n📋 Проверяем файлы...")
    for file in required_files:
        if os.path.exists(file):
            print(f"   ✅ {file} существует")
        else:
            print(f"   ❌ {file} ОТСУТСТВУЕТ")
    
    print("\n🔄 Тестируем импорты...")
    if test_imports():
        print("\n🎉 Все основные импорты работают!")
        print("Пробуем запустить бота...")
        
        try:
            import asyncio
            from bot import main as bot_main
            
            # Запускаем в отдельном потоке с таймаутом
            async def run_with_timeout():
                try:
                    await asyncio.wait_for(bot_main(), timeout=10.0)
                except asyncio.TimeoutError:
                    print("⏰ Таймаут - бот работает нормально")
                except Exception as e:
                    print(f"💥 Ошибка при запуске бота: {e}")
                    traceback.print_exc()
            
            asyncio.run(run_with_timeout())
            
        except Exception as e:
            print(f"💥 Критическая ошибка при запуске: {e}")
            traceback.print_exc()
    else:
        print("\n❌ Есть проблемы с импортами")
    
    input("\n⏸️ Нажмите Enter для выхода...")

if __name__ == "__main__":
    main()