import speech_recognition as sr
import logging
from pathlib import Path
from typing import Optional
import string

from config import config

logger = logging.getLogger(__name__)


class SpeechRecognitionService:
    """Сервис для распознавания речи из голосовых сообщений."""

    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.language = config.SPEECH_RECOGNITION_LANGUAGE
        logger.info(f"SpeechRecognitionService инициализирован с языком: {self.language}")



    async def recognize_speech(self, audio_file_path: Path) -> Optional[str]:
        """
        Распознавание речи из аудиофайла.
        """
        try:
            # Проверяем что файл существует
            if not audio_file_path.exists():
                logger.error("Аудиофайл не существует!")
                return None

            file_size = audio_file_path.stat().st_size
            if file_size == 0:
                logger.error("Аудиофайл пустой!")
                return None

            logger.info(f"Размер аудиофайла: {file_size} bytes")

            with sr.AudioFile(str(audio_file_path)) as source:
                # Настраиваем для фонового шума
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)

                # Читаем аудио данные
                audio_data = self.recognizer.record(source)

                # Пытаемся распознать через Google
                try:
                    text = self.recognizer.recognize_google(audio_data, language=self.language)
                    logger.info(f"Распознанный текст: '{text}'")
                    return text
                except sr.UnknownValueError:
                    logger.warning("Речь не распознана (UnknownValueError)")
                    return None
                except sr.RequestError as e:
                    logger.error(f"Ошибка сервиса распознавания речи: {e}")
                    return None

        except Exception as e:
            logger.error(f"Неожиданная ошибка при распознавании речи: {e}")
            return None

    def check_answer(self, user_answer: str, correct_answer: str) -> bool:
        """
        Улучшенная проверка ответа пользователя с нормализацией.
        """

        def normalize_text(text: str) -> str:
            """Нормализует текст для сравнения"""
            if not text:
                return ""

            # Приводим к нижнему регистру
            text = text.lower().strip()

            # Заменяем ё на е
            text = text.replace('ё', 'е')

            # Убираем знаки препинания
            text = text.translate(str.maketrans('', '', string.punctuation))

            # Убираем лишние пробелы
            text = ' '.join(text.split())

            return text

        if not user_answer or not correct_answer:
            logger.warning("Пустой ответ или фраза для проверки")
            return False

        # Нормализуем оба текста
        user_norm = normalize_text(user_answer)
        correct_norm = normalize_text(correct_answer)

        logger.info(f"Проверка (нормализовано): '{user_norm}' vs '{correct_norm}'")

        # 1. Полное совпадение после нормализации
        if user_norm == correct_norm:
            logger.info("✅ Ответ совпадает полностью после нормализации")
            return True

        # 2. Разбиваем на слова для более гибкого сравнения
        user_words = user_norm.split()
        correct_words = correct_norm.split()

        # 3. Проверяем что ответ не слишком короткий
        if len(user_words) < len(correct_words) * 0.4:
            logger.warning("Ответ слишком короткий")
            return False

        # 4. Ищем важные слова (длиннее 3 символов)
        important_words = [word for word in correct_words if len(word) > 3]

        # Если нет важных слов, используем все слова
        if not important_words:
            important_words = correct_words

        # 5. Проверяем что все важные слова присутствуют
        matches = 0
        for important_word in important_words:
            if any(important_word == user_word for user_word in user_words):
                matches += 1

        # Должны совпасть все важные слова
        all_match = matches == len(important_words)

        logger.info(f"Совпадения важных слов: {matches}/{len(important_words)}, все совпали: {all_match}")

        return all_match


# Глобальный экземпляр сервиса
speech_service = SpeechRecognitionService()






