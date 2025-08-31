from aiogram import Bot
from config import config


async def notify_operator(bot: Bot, user_id: int, username: str, user_message: str):
    """
    Отправляет уведомление оператору о новом запросе.
    """
    if not config.ADMIN_ID:
        print("ADMIN_ID не задан. Уведомление не отправлено.")
        return

    message_text = (
        "🔔 *Новый запрос в поддержку!*\n"
        f"*От пользователя:* [{username}](tg://user?id={user_id})\n"
        f"*Его ID:* `{user_id}`\n"
        f"*Сообщение:*\n_{user_message}_"
    )

    try:
        await bot.send_message(
            chat_id=config.ADMIN_ID,
            text=message_text,
            parse_mode="Markdown"
        )
    except Exception as e:
        print(f"Не удалось отправить сообщение оператору: {e}")