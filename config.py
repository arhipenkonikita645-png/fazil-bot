import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_IDS = list(map(int, os.getenv('ADMIN_IDS', '').split(','))) if os.getenv('ADMIN_IDS') else []
MAIN_ADMIN_ID = int(os.getenv('MAIN_ADMIN_ID')) if os.getenv('MAIN_ADMIN_ID') else None
ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', '@admin')