from pathlib import Path
from gtts import gTTS
import os

# Указываем путь напрямую
AUDIO_PHRASES_DIR = Path("audio/phrases")


def create_test_audio_files():
    """Создание тестовых аудиофайлов."""
    # Создаем директорию если не существует
    AUDIO_PHRASES_DIR.mkdir(parents=True, exist_ok=True)

    phrases = {
        "phrase_1": "Привет, как дела?",
        "phrase_2": "Сегодня хорошая погода",
        "phrase_3": "Я изучаю иностранный язык"
    }

    print("Создание тестовых аудиофайлов...")
    print(f"Директория для сохранения: {AUDIO_PHRASES_DIR}")

    for phrase_id, text in phrases.items():
        audio_path = AUDIO_PHRASES_DIR / f"{phrase_id}.mp3"

        if not audio_path.exists():
            try:
                print(f"Создаю аудиофайл: {phrase_id} - '{text}'")
                tts = gTTS(text=text, lang='ru', slow=False)
                tts.save(str(audio_path))
                print(f"✅ Успешно создан: {audio_path.name}")
            except Exception as e:
                print(f"❌ Ошибка создания файла {phrase_id}: {e}")
        else:
            print(f"📁 Файл уже существует: {audio_path.name}")

    print("\nГотово! Проверьте созданные файлы.")


if __name__ == "__main__":
    create_test_audio_files()