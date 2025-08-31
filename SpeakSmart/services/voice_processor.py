
import logging
import os
import speech_recognition as sr
from pydub import AudioSegment
import tempfile

logger = logging.getLogger(__name__)


class VoiceProcessor:
    def __init__(self):
        self.recognizer = sr.Recognizer()

    async def process_voice_message(self, voice_file_path: str) -> str:
        """
        Пытается распознать голосовое сообщение разными способами
        """
        try:
            # Конвертируем OGG в WAV
            if voice_file_path.endswith('.oga') or voice_file_path.endswith('.ogg'):
                audio = AudioSegment.from_file(voice_file_path, format="ogg")  # ← ИСПРАВЛЕНО
                wav_path = voice_file_path.rsplit('.', 1)[0] + '.wav'
                audio.export(wav_path, format="wav")
                voice_file_path = wav_path

            # Распознаем речь
            with sr.AudioFile(voice_file_path) as source:
                audio_data = self.recognizer.record(source)

            # Попытка 1: Google Speech Recognition
            try:
                text = self.recognizer.recognize_google(audio_data, language='ru-RU')
                logger.info(f"Google распознал: {text}")
                return text.lower()
            except sr.UnknownValueError:
                logger.warning("Google не распознал речь")
                return ""
            except sr.RequestError as e:
                logger.error(f"Ошибка запроса к Google: {e}")
                return ""

        except Exception as e:
            logger.error(f"Ошибка обработки голоса: {e}")
            return ""
        finally:
            # Удаляем временные файлы
            try:
                if os.path.exists(voice_file_path):
                    os.remove(voice_file_path)
            except Exception as e:
                logger.warning(f"Не удалось удалить временный файл: {e}")


# Создаем глобальный экземпляр
voice_processor = VoiceProcessor()