import logging
from aiogram import Router, types, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, Optional, ReplyKeyboardMarkup, KeyboardButton, FSInputFile
from pathlib import Path

from services.database import db
from services.speech_recognition import speech_service
from services.tts_service import tts_service
from config import config

logger = logging.getLogger(__name__)
router = Router()


class PracticeStates(StatesGroup):
    """Состояния для режима практики."""
    waiting_for_response = State()
    practicing = State()
    waiting_for_text_input = State()  # НОВОЕ СОСТОЯНИЕ: ожидание текстового ввода


practice_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🎯 Новая фраза"), KeyboardButton(text="🔁 Повторить")],
        [KeyboardButton(text="📊 Статистика"), KeyboardButton(text="🚪 Выход")]
    ],
    resize_keyboard=True
)

# Упрощенная клавиатура для ответа
response_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🎤 Ответить голосом"), KeyboardButton(text="💬 Ответить текстом")],
        [KeyboardButton(text="🚪 Выход")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

# НОВАЯ КЛАВИАТУРА: для текстового ввода
text_input_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="❌ Отменить текстовый ввод")]
    ],
    resize_keyboard=True
)


@router.message(Command("practice"))
async def cmd_practice(message: types.Message, state: FSMContext):
    """Обработчик команды /practice - начало языковой практики."""
    try:
        user_id = message.from_user.id
        logger.info(f"User {user_id} started /practice")

        # Устанавливаем состояние practicing и сбрасываем данные
        await state.set_state(PracticeStates.practicing)
        await state.update_data(
            correct_answers=0,
            total_attempts=0,
            current_phrase=None,
            current_phrase_id=None
        )

        welcome_text = (
            "🎯 *Режим языковой практики*\n\n"
            "Я буду отправлять вам голосовые фразы, "
            "а вы попробуйте повторить их!\n\n"
            "📝 *Как это работает:*\n"
            "1. Я отправляю голосовое сообщение с фразой\n"
            "2. Вы отправляете голосовое сообщение с ответом\n"
            "3. Я проверяю ваш ответ и даю обратную связь\n\n"
            "Используйте кнопки ниже для управления практикой."
        )

        await message.answer(welcome_text, reply_markup=practice_keyboard)
        await message.answer("Нажмите *'🎯 Новая фраза'*, чтобы начать!", reply_markup=practice_keyboard)

    except Exception as e:
        logger.error(f"Error in cmd_practice: {e}")
        await message.answer("❌ Не удалось запустить режим практики.")
        await state.clear()


async def send_practice_phrase(message: types.Message, state: FSMContext):
    """Отправка фразы для практики и переход в состояние ожидания."""
    user_id = message.from_user.id
    logger.info(f"Sending phrase to user {user_id}")

    try:
        phrase_id, phrase_text = tts_service.get_random_phrase()
        if not phrase_text:
            await message.answer("❌ Не удалось загрузить фразу для практики. Попробуйте позже.")
            return

        logger.info(f"Phrase for user {user_id}: {phrase_text}")

        # Сохраняем текущую фразу в состоянии
        await state.update_data(
            current_phrase=phrase_text,
            current_phrase_id=phrase_id
        )

        # Отправляем текстовую версию фразы
        await message.answer(f"📝 *Фраза для повторения:*\n`{phrase_text}`")

        # Пытаемся отправить голосовое сообщение
        audio_path = tts_service.get_phrase_audio_path(phrase_id)
        if audio_path and audio_path.exists():
            try:
                voice = FSInputFile(audio_path)
                await message.answer_voice(
                    voice=voice,
                    caption="🎧 Прослушайте и повторите эту фразу"
                )
            except Exception as e:
                logger.error(f"Error sending voice: {e}")
                await message.answer("❌ Не удалось отправить голосовое сообщение.")
        else:
            logger.warning(f"Audio file not found: {audio_path}")
            await message.answer("🔇 *Аудио временно недоступно.* Повторите фразу текстом.")

        # Просим пользователя ответить
        await message.answer(
            "*Выберите способ ответа:*",
            reply_markup=response_keyboard
        )

        # Меняем состояние на ожидание ответа
        await state.set_state(PracticeStates.waiting_for_response)

    except Exception as e:
        logger.error(f"Error in send_practice_phrase: {e}")
        await message.answer("❌ Произошла ошибка при подготовке фразы.")
        await state.set_state(PracticeStates.practicing)


# Обработчик для кнопки "🎤 Ответить голосом"
@router.message(PracticeStates.waiting_for_response, F.text == "🎤 Ответить голосом")
async def handle_voice_prompt(message: types.Message, state: FSMContext):
    """Пользователь готовит голосовой ответ."""
    await message.answer(
        "Отлично! Теперь просто отправьте голосовое сообщение с вашим ответом. 🎤",
        reply_markup=types.ReplyKeyboardRemove()  # Убираем клавиатуру, чтобы не мешала
    )


# Обработчик для кнопки "💬 Ответить текстом"
@router.message(PracticeStates.waiting_for_response, F.text == "💬 Ответить текстом")
async def handle_text_prompt(message: types.Message, state: FSMContext):
    """Пользователь готовит текстовый ответ."""
    await message.answer(
        "Хорошо! Напишите текст фразы, которую вы услышали. 💬",
        reply_markup=text_input_keyboard  # Используем специальную клавиатуру
    )
    # Переходим в состояние ожидания текстового ввода
    await state.set_state(PracticeStates.waiting_for_text_input)


# НОВЫЙ ОБРАБОТЧИК: Для кнопки "❌ Отменить текстовый ввод"
@router.message(PracticeStates.waiting_for_text_input, F.text == "❌ Отменить текстовый ввод")
async def handle_cancel_text_input(message: types.Message, state: FSMContext):
    """Отмена текстового ввода и возврат к выбору способа ответа."""
    await message.answer(
        "Текстовый ввод отменен. Выберите способ ответа:",
        reply_markup=response_keyboard
    )
    await state.set_state(PracticeStates.waiting_for_response)


# НОВЫЙ ОБРАБОТЧИК: Для текстового ответа в специальном состоянии
@router.message(PracticeStates.waiting_for_text_input, F.text)
async def handle_text_input_response(message: types.Message, state: FSMContext):
    """Обработка текстового ответа пользователя в состоянии текстового ввода."""
    user_text = message.text.strip()

    # Если пользователь нажал кнопку отмены - уже обработано выше
    if user_text == "❌ Отменить текстовый ввод":
        return

    # Обрабатываем как ответ на фразу
    await process_user_response(message, state, user_text, is_voice=False)


@router.message(PracticeStates.waiting_for_response, F.voice)
async def handle_voice_response(message: types.Message, state: FSMContext):
    """Обработка голосового ответа пользователя"""
    try:
        user_id = message.from_user.id
        logger.info(f"User {user_id} отправил голосовое сообщение")

        await message.answer(
            "🎤 Голосовое сообщение получено! \n\n"
            "Для точной проверки произношения, пожалуйста, "
            "**дополнительно отправьте текст той фразы, которую вы сказали**. \n\n"
            "Это поможет мне проверить ваш ответ точнее!",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[[KeyboardButton(text="💬 Ввести текст произношения")]],
                resize_keyboard=True
            )
        )

        # Сохраняем информацию о голосовом сообщении для последующей проверки
        await state.update_data(has_voice_response=True)

    except Exception as e:
        logger.error(f"Ошибка обработки голосового сообщения: {e}")
        await message.answer("❌ Произошла ошибка при обработке голосового сообщения.")


# НОВЫЙ ОБРАБОТЧИК: Для кнопки "💬 Ввести текст произношения" после голосового сообщения
@router.message(PracticeStates.waiting_for_response, F.text == "💬 Ввести текст произношения")
async def handle_text_after_voice(message: types.Message, state: FSMContext):
    """Обработка нажатия кнопки текстового ввода после голосового сообщения."""
    await message.answer(
        "Хорошо! Напишите текст фразы, которую вы произнесли. 💬",
        reply_markup=text_input_keyboard
    )
    # Переходим в состояние ожидания текстового ввода
    await state.set_state(PracticeStates.waiting_for_text_input)


@router.message(PracticeStates.waiting_for_response, F.text)
async def handle_text_response(message: types.Message, state: FSMContext):
    """Обработка текстового ответа пользователя."""
    user_id = message.from_user.id
    user_text = message.text.strip()
    logger.info(f"User {user_id} sent text response: '{user_text}'")

    # Команда из клавиатуры, выходим из состояния ожидания
    if user_text in ["🚪 Выход"]:
        await handle_exit(message, state)
        return

    # Обрабатываем как ответ
    await process_user_response(message, state, user_text, is_voice=False)


# Вынесена общая логика проверки ответа
async def process_user_response(message: types.Message, state: FSMContext, user_response: str, is_voice: bool):
    """Общая функция для обработки и проверки ответа пользователя."""
    try:
        user_id = message.from_user.id
        state_data = await state.get_data()

        current_phrase = state_data.get('current_phrase')
        current_phrase_id = state_data.get('current_phrase_id')
        correct_answers = state_data.get('correct_answers', 0)
        total_attempts = state_data.get('total_attempts', 0) + 1

        if not current_phrase:
            await message.answer("❌ Ошибка: фраза не найдена. Начните заново.", reply_markup=practice_keyboard)
            await state.set_state(PracticeStates.practicing)
            return

        # Проверяем ответ
        is_correct = speech_service.check_answer(user_response, current_phrase)
        logger.info(f"Check result for user {user_id}: {is_correct}")

        # Сохраняем в базу
        db.add_practice_session(user_id, current_phrase_id, user_response, is_correct)

        # Обновляем статистику
        if is_correct:
            correct_answers += 1
            feedback = "✅ *Отлично!* Правильный ответ!\n\n"
        else:
            feedback = "❌ *Попробуйте ещё раз!*\n"
            feedback += f"*Ваш ответ:* {user_response}\n"
            feedback += f"*Правильный ответ:* {current_phrase}\n\n"

        # Сохраняем новую статистику
        await state.update_data(
            correct_answers=correct_answers,
            total_attempts=total_attempts
        )

        # Добавляем статистику в фидбек
        accuracy = (correct_answers / total_attempts * 100) if total_attempts > 0 else 0
        feedback += f"📊 *Статистика:*\n"
        feedback += f"Правильных ответов: {correct_answers}/{total_attempts}\n"
        feedback += f"Точность: {accuracy:.1f}%"

        await message.answer(feedback, reply_markup=practice_keyboard)
        # Возвращаем пользователя в состояние "практики"
        await state.set_state(PracticeStates.practicing)

    except Exception as e:
        logger.error(f"Error processing response: {e}")
        await message.answer("❌ Произошла ошибка при проверке ответа.", reply_markup=practice_keyboard)
        await state.set_state(PracticeStates.practicing)


# Обработчики кнопок управления практикой
@router.message(PracticeStates.practicing, F.text == "🎯 Новая фраза")
async def handle_new_phrase(message: types.Message, state: FSMContext):
    await send_practice_phrase(message, state)


@router.message(PracticeStates.practicing, F.text == "🔁 Повторить")
async def handle_repeat_phrase(message: types.Message, state: FSMContext):
    state_data = await state.get_data()
    current_phrase = state_data.get('current_phrase')
    if current_phrase:
        await message.answer(f"🔁 *Повтор фразы:*\n`{current_phrase}`")
        await message.answer("Выберите способ ответа:", reply_markup=response_keyboard)
        await state.set_state(PracticeStates.waiting_for_response)
    else:
        await send_practice_phrase(message, state)


@router.message(PracticeStates.practicing, F.text == "📊 Статистика")
async def handle_statistics(message: types.Message, state: FSMContext):
    state_data = await state.get_data()
    correct_answers = state_data.get('correct_answers', 0)
    total_attempts = state_data.get('total_attempts', 0)
    accuracy = (correct_answers / total_attempts * 100) if total_attempts > 0 else 0
    stats_text = f"📊 *Ваша статистика практики:*\n\n✅ Правильных ответов: *{correct_answers}*\n📝 Всего попыток: *{total_attempts}*\n🎯 Точность: *{accuracy:.1f}%*\n\nПродолжайте практиковаться!"
    await message.answer(stats_text)


@router.message(F.text == "🚪 Выход")
@router.message(PracticeStates.practicing, F.text == "🚪 Выход")
async def handle_exit(message: types.Message, state: FSMContext):
    """Выход из режима практики."""
    state_data = await state.get_data()
    correct_answers = state_data.get('correct_answers', 0)
    total_attempts = state_data.get('total_attempts', 0)
    goodbye_text = f"👋 *Завершение практики*\n\n✅ Правильных ответов: *{correct_answers}*\n📝 Всего попыток: *{total_attempts}*\n\nВозвращайтесь для дальнейшей практики!"
    await message.answer(goodbye_text, reply_markup=types.ReplyKeyboardRemove())
    await state.clear()


async def download_voice_message(file_id: str, user_id: int) -> Optional[Path]:
    """
    Скачивание голосового сообщения из Telegram.
    """
    try:
        from aiogram import Bot
        from config import config
        import os
        from pathlib import Path

        # Создаем временную папку для аудио
        temp_dir = Path("temp_audio")
        temp_dir.mkdir(exist_ok=True)

        # Создаем экземпляр бота
        bot = Bot(token=config.BOT_TOKEN)

        # Скачиваем файл
        file = await bot.get_file(file_id)
        file_path = file.file_path

        # Создаем путь для сохранения
        download_path = temp_dir / f"voice_{user_id}_{file_id}.ogg"

        # Скачиваем файл
        await bot.download_file(file_path, destination=str(download_path))

        logger.info(f"Голосовое сообщение скачано: {download_path}")

        # Проверяем, что файл действительно создался
        if download_path.exists():
            await bot.session.close()  # Закрываем сессию
            return download_path
        else:
            logger.error(f"Файл не был создан: {download_path}")
            await bot.session.close()  # Закрываем сессию
            return None

    except Exception as e:
        logger.error(f"Ошибка скачивания голосового сообщения {file_id}: {e}")
        return None


def register_practice_handlers(dp):
    dp.include_router(router)