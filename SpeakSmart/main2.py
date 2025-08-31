import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from config import config
from services.database import db
from utils.logger import setup_logging

# Настройка логирования

try:
    setup_logging()
except ImportError:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("bot.log"),
            logging.StreamHandler()
        ]
    )

logger = logging.getLogger(__name__)

async def register_handlers(dp: Dispatcher):
    """Регистрация всех обработчиков."""
    try:
        # Импортируем и регистрируем обработчики
        # Импорт делаем ЗДЕСЬ, чтобы избежать циклических импортов
        from handlers.start import register_start_handlers
        from handlers.common import register_common_handlers
        from handlers.practice import register_practice_handlers
        from handlers.support import register_support_handlers

        register_start_handlers(dp)
        register_common_handlers(dp)
        register_practice_handlers(dp)
        register_support_handlers(dp)

        logger.info("Все обработчики успешно зарегистрированы")
        return True
    except Exception as e:
        logger.error(f"Ошибка регистрации обработчиков: {e}")
        return False

async def on_startup():
    """Действия при запуске бота."""
    logger.info("Бот запускается...")
    # Здесь можно добавить инициализацию БД, если нужно
    # await db.init()

async def on_shutdown():
    """Действия при остановке бота."""
    logger.info("Бот останавливается...")
    # Здесь можно добавить корректное закрытие соединений с БД, если нужно
    # await db.close()

async def main():
    """Основная функция запуска бота."""
    try:
        # Инициализация бота и диспетчера
        bot = Bot(
            token=config.BOT_TOKEN,
            default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN)
        )
        storage = MemoryStorage()
        dp = Dispatcher(storage=storage)

        # Подключаем обработчики startup/shutdown
        dp.startup.register(on_startup)
        dp.shutdown.register(on_shutdown)

        # Регистрируем все хэндлеры
        await register_handlers(dp)

        logger.info("Запуск бота в режиме polling...")
        await dp.start_polling(bot)

    except Exception as e:
        logger.error(f"Критическая ошибка: {e}", exc_info=True)
    finally:
        if 'bot' in locals():
            await bot.session.close()
        logger.info("Бот завершил работу.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"Неожиданная ошибка при запуске: {e}", exc_info=True)