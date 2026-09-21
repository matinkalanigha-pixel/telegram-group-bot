import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
DB_PATH = os.getenv("DB_PATH", "bot_data.db")

if not BOT_TOKEN:
    raise RuntimeError(
        "توکن بات تنظیم نشده! یک فایل .env بساز و مقدار BOT_TOKEN را در آن قرار بده."
    )
