import sys

def check_dependencies():
    print("🔍 Проверка зависимостей...")
    
    dependencies = [
        ('aiogram', '3.2.0'),
        ('python-dotenv', '1.0.0'),
        ('aiohttp', '3.8.0'),
        ('sqlite3', 'built-in')
    ]
    
    all_ok = True
    
    for package, expected_version in dependencies:
        try:
            if package == 'sqlite3':
                import sqlite3
                version = sqlite3.version
            else:
                module = __import__(package)
                version = getattr(module, '__version__', 'unknown')
            
            print(f"✅ {package}: {version}")
            
        except ImportError:
            print(f"❌ {package}: НЕ УСТАНОВЛЕН")
            all_ok = False
    
    print(f"\n📊 Результат: {'ВСЕ ЗАВИСИМОСТИ УСТАНОВЛЕНЫ' if all_ok else 'ЕСТЬ ПРОБЛЕМЫ С ЗАВИСИМОСТЯМИ'}")
    
    if not all_ok:
        print("\n💡 Установите недостающие зависимости:")
        print("pip install aiogram==3.2.0 python-dotenv")

if __name__ == "__main__":
    check_dependencies()