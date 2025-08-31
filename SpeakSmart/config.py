import os
import json
from pathlib import Path
from aiogram.enums import ParseMode
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

class Config:
    """Конфигурационные параметры бота."""

    # Токен бота от @BotFather
    BOT_TOKEN = os.getenv("BOT_TOKEN", "8232111481:AAEPgTYgammOzQplrzCBqcq7M-Oy-GpZkyY")

    # ID администратора/оператора
    ADMIN_ID = int(os.getenv("ADMIN_ID", 1978359710))

    # Настройки базы данных
    DATABASE_PATH = "data/database.db"

    # Пути к файлам
    BASE_DIR = Path(__file__).parent
    AUDIO_PHRASES_DIR = BASE_DIR / "audio" / "phrases"
    USER_RESPONSES_DIR = BASE_DIR / "audio" / "user_responses"
    TEMP_AUDIO_DIR = BASE_DIR / "audio" / "temp"
    FAQ_FILE = BASE_DIR / "data" / "faq.json"

    # Настройки распознавания речи
    SPEECH_RECOGNITION_LANGUAGE = "en-US"

    # Настройки бота
    BOT_PROPERTIES = {
        "parse_mode": ParseMode.MARKDOWN
    }

    @classmethod
    def load_faq(cls):
        """Загружает данные FAQ из JSON файла."""
        try:
            if cls.FAQ_FILE.exists():
                with open(cls.FAQ_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                print(f"⚠️ Файл FAQ не найден: {cls.FAQ_FILE}")
                return {"faq": []}
        except json.JSONDecodeError as e:
            print(f"❌ Ошибка чтения FAQ файла: {e}")
            return {"faq": []}
        except Exception as e:
            print(f"❌ Неожиданная ошибка при загрузке FAQ: {e}")
            return {"faq": []}

    # Данные FAQ
    FAQ_DATA = None


# Создаем директории
os.makedirs(Config.AUDIO_PHRASES_DIR, exist_ok=True)
os.makedirs(Config.USER_RESPONSES_DIR, exist_ok=True)
os.makedirs(Config.TEMP_AUDIO_DIR, exist_ok=True)
os.makedirs(os.path.dirname(Config.DATABASE_PATH), exist_ok=True)
os.makedirs(os.path.dirname(Config.FAQ_FILE), exist_ok=True)

# Ззагружаем FAQ данные
Config.FAQ_DATA = Config.load_faq()

config = Config()






