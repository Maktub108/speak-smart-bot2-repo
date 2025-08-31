
import os
from pathlib import Path
from gtts import gTTS


def generate_audio_files():
    """Генерирует аудиофайлы для английских фраз через gTTS"""

    # Словарь фраз для генерации
    PHRASES = {
        "greeting_hello": "Hello!",
        "question_name": "What is your name?",
        "question_english": "Do you speak English?",
        "thanks": "Thank you.",
        "goodbye": "Goodbye!",
        "morning": "Good morning.",
        "evening": "Good evening.",
        "question_mood": "How are you?"
    }

    # Создаем папку для аудио
    audio_dir = Path("audio/phrases")
    audio_dir.mkdir(parents=True, exist_ok=True)

    print("🎵 Начинаем генерацию аудиофайлов...\n")

    for phrase_id, phrase_text in PHRASES.items():
        try:
            # Создаем путь к файлу
            file_path = audio_dir / f"{phrase_id}.mp3"

            # Пропускаем если файл уже существует
            if file_path.exists():
                print(f"📁 Уже существует: {phrase_text} -> {file_path}")
                continue

            # Генерируем аудио через Google TTS
            tts = gTTS(text=phrase_text, lang='en', slow=False)
            tts.save(str(file_path))

            print(f"✅ Сгенерировано: {phrase_text} -> {file_path}")

        except Exception as e:
            print(f"❌ Ошибка при генерации {phrase_text}: {e}")

    print("\n🎉 Генерация завершена!")
    print(f"📁 Файлы сохранены в: {audio_dir.absolute()}")


if __name__ == "__main__":
    generate_audio_files()