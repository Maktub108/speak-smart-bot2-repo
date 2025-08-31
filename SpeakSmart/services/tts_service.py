import logging
from pathlib import Path
from typing import Optional
import random

from config import config

logger = logging.getLogger(__name__)


class TTSService:
    """Сервис для работы с аудиофразами."""

    def __init__(self):
        self.audio_phrases = {
            "greeting_hello": {
                "text": "Hello!",
                "correct_answers": ["hello", "hi", "hey", "hi there", "hello there"]
            },
            "question_name": {
                "text": "What is your name?",
                "correct_answers": ["my name is", "i am", "it is", "you can call me", "name is"]
            },
            "question_english": {
                "text": "Do you speak English?",
                "correct_answers": ["yes i do", "yes", "a little", "i am learning", "i speak english", "of course"]
            },
            "thanks": {
                "text": "Thank you.",
                "correct_answers": ["you are welcome", "welcome", "my pleasure", "no problem", "sure", "anytime"]
            },
            "goodbye": {
                "text": "Goodbye!",
                "correct_answers": ["goodbye", "bye", "see you", "see you later", "take care", "bye bye"]
            },
            "morning": {
                "text": "Good morning.",
                "correct_answers": ["good morning", "morning", "good morning to you", "have a good morning"]
            },
            "evening": {
                "text": "Good evening.",
                "correct_answers": ["good evening", "evening", "good evening to you", "have a good evening"]
            },
            "question_mood": {
                "text": "How are you?",
                "correct_answers": ["i am fine", "fine", "good", "great", "ok", "not bad", "i am good"]
            }
        }

        logger.info("TTSService инициализирован")

    def get_random_phrase(self) -> tuple[str, str]:
        """Получение случайной фразы для практики."""
        phrase_id = random.choice(list(self.audio_phrases.keys()))
        phrase_data = self.audio_phrases[phrase_id]
        logger.info(f"Выбрана фраза: {phrase_id} - {phrase_data['text']}")
        return phrase_id, phrase_data["text"]

    def get_phrase_audio_path(self, phrase_id: str) -> Optional[Path]:
        """Получение пути к аудиофайлу фразы."""
        if phrase_id in self.audio_phrases:
            # ИЗМЕНИЛИ ПУТЬ: используем прямую структуру audio/phrases/
            audio_path = Path(f"audio/phrases/{phrase_id}.mp3")

            logger.info(f"Поиск аудиофайла: {audio_path}")

            if audio_path.exists():
                logger.info(f"Аудиофайл найден: {audio_path}")
                return audio_path
            else:
                logger.warning(f"Аудиофайл не найден: {audio_path}")
                return None
        return None

    def get_phrase_text(self, phrase_id: str) -> Optional[str]:
        """Получение текста фразы."""
        if phrase_id in self.audio_phrases:
            return self.audio_phrases[phrase_id]["text"]
        return None


# Глобальный экземпляр сервиса
tts_service = TTSService()