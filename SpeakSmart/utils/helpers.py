import re


def check_answer(user_answer: str, expected_keywords: list) -> bool:
    """
    Гибкая проверка ответа: достаточно совпадения с ЛЮБОЙ группой ключевых слов
    """
    if not expected_keywords or not user_answer:
        return False

    # Очищаем текст
    cleaned_text = re.sub(r'[^\w\s]', ' ', user_answer.lower())
    cleaned_text = ' '.join(cleaned_text.split())
    user_words = cleaned_text.split()

    # Проверяем, есть ли совпадение с ХОТЯ БЫ ОДНОЙ группой
    for keyword_group in expected_keywords:
        for keyword in keyword_group:
            if keyword in user_words:
                return True  # Достаточно одного совпадения с любой группой

    return False


def strict_check_answer(user_answer: str, expected_keywords: list) -> bool:
    """
    Строгая проверка: должны быть слова из ВСЕХ групп (старая логика)
    """
    if not expected_keywords or not user_answer:
        return False

    cleaned_text = re.sub(r'[^\w\s]', ' ', user_answer.lower())
    cleaned_text = ' '.join(cleaned_text.split())
    user_words = cleaned_text.split()

    # Должны быть слова из КАЖДОЙ группы
    for keyword_group in expected_keywords:
        group_found = False
        for keyword in keyword_group:
            if keyword in user_words:
                group_found = True
                break

        if not group_found:
            return False

    return True