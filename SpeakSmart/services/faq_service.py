import re
from config import config


def find_answer(user_message: str) -> str | None:
    user_message = user_message.lower().strip()

    for item in config.FAQ_DATA.get('faq', []):
        for keyword in item.get('keywords', []):
            pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
            if re.search(pattern, user_message):
                return item.get('answer')
    return None