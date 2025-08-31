import logging
import requests
import os
import aiohttp
import aiofiles
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

logger = logging.getLogger(__name__)


class YandexSpeechKit:
    def __init__(self):
        self.api_key = os.getenv("YANDEX_API_KEY") or os.getenv("API_KEY")
        self.folder_id = os.getenv("YANDEX_FOLDER_ID") or os.getenv("FOLDER_ID")
        self.base_url = "https://stt.api.cloud.yandex.net/speech/v1/stt:recognize"

        # Логируем для отладки
        logger.info(f"Yandex SpeechKit инициализирован. Folder ID: {self.folder_id}")

    async def process_voice_message(self, voice_file_path: str) -> str:
        """Основной метод для обработки голосовых сообщений"""
        return await self.recognize_speech(voice_file_path)

    async def recognize_speech(self, audio_file_path: str) -> str:
        """Распознает речь из аудио файла"""
        try:
            # Проверяем наличие ключей
            if not self.api_key:
                logger.error("YANDEX_API_KEY не настроен!")
                return ""
            if not self.folder_id:
                logger.error("YANDEX_FOLDER_ID не настроен!")
                return ""

            # Читаем аудио файл
            async with aiofiles.open(audio_file_path, 'rb') as audio_file:
                audio_data = await audio_file.read()

            headers = {
                "Authorization": f"Api-Key {self.api_key}",
                "Content-Type": "audio/ogg"
            }

            params = {
                "folderId": self.folder_id,
                "lang": "ru-RU"
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                        self.base_url,
                        headers=headers,
                        params=params,
                        data=audio_data,
                        timeout=10
                ) as response:

                    logger.info(f"Yandex SpeechKit response: {response.status}")

                    if response.status == 200:
                        result = await response.json()
                        recognized_text = result.get("result", "")
                        logger.info(f"Yandex SpeechKit распознал: {recognized_text}")
                        return recognized_text.lower()
                    else:
                        error_text = await response.text()
                        logger.error(f"Ошибка Yandex SpeechKit: {error_text}")
                        return ""

        except Exception as e:
            logger.error(f"Ошибка в Yandex SpeechKit: {e}")
            return ""
        finally:
            # Очищаем временный файл
            try:
                if os.path.exists(audio_file_path):
                    os.remove(audio_file_path)
            except Exception as e:
                logger.warning(f"Не удалось удалить временный файл: {e}")


# Создаем глобальный экземпляр
yandex_speech = YandexSpeechKit()