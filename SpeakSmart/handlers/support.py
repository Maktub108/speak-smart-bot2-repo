from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command, StateFilter

from services.faq_service import find_answer
from services.operator_service import notify_operator

# Создаем роутер
support_router = Router()


@support_router.message(Command("support"))
async def cmd_support(message: Message):
    welcome_text = (
        "💬 *Режим поддержки*\n\n"
        "Опишите свой вопрос текстом, и я постараюсь помочь. "
        "Если я не найду ответ, то передам ваш вопрос живому оператору."
    )
    await message.answer(welcome_text, parse_mode="Markdown")


@support_router.message(StateFilter(None), F.text)
async def handle_text_message(message: Message, bot):
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name
    user_message = message.text

    # 1. Пытаемся найти ответ в FAQ
    answer = find_answer(user_message)

    if answer:
        # Отправляем пользователю
        await message.answer(answer)
    else:
        # 2. Если ответа нет, уведомляем оператора
        await notify_operator(bot, user_id, username, user_message)

        # 3. Сообщаем пользователю о передаче оператору
        await message.answer(
            "❓ Я пока не знаю ответ на этот вопрос.\n"
            "Ваш запрос был передан живому оператору. Ожидайте, с вами свяжутся в ближайшее время."
        )


# Функция для регистрации обработчиков
def register_support_handlers(dp):
    """Регистрация обработчиков поддержки"""
    dp.include_router(support_router)