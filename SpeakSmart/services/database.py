import sqlite3
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

from config import config

logger = logging.getLogger(__name__)


class Database:
    """Класс для работы с SQLite базой данных."""

    def __init__(self, db_path: str = config.DATABASE_PATH):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Инициализация базы данных и создание таблиц."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Таблица пользователей
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        user_id INTEGER PRIMARY KEY,
                        username TEXT,
                        first_name TEXT,
                        last_name TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')

                # Таблица сессий практики
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS practice_sessions (
                        session_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        phrase_id TEXT,
                        user_response TEXT,
                        is_correct BOOLEAN,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (user_id)
                    )
                ''')

                # Таблица запросов поддержки
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS support_requests (
                        request_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        question TEXT,
                        response TEXT,
                        is_escalated BOOLEAN DEFAULT FALSE,
                        operator_id INTEGER,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        resolved_at TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (user_id)
                    )
                ''')

                # Таблица логов ошибок
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS error_logs (
                        log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        error_message TEXT,
                        stack_trace TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')

                conn.commit()
                logger.info("База данных успешно инициализирована")

        except sqlite3.Error as e:
            logger.error(f"Ошибка инициализации базы данных: {e}")
            raise

    def add_user(self, user_id: int, username: str, first_name: str, last_name: str = None):
        """Добавление нового пользователя в базу."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR IGNORE INTO users (user_id, username, first_name, last_name)
                    VALUES (?, ?, ?, ?)
                ''', (user_id, username, first_name, last_name))
                conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Ошибка добавления пользователя: {e}")

    def update_user_activity(self, user_id: int):
        """Обновление времени последней активности пользователя."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE users SET last_activity = CURRENT_TIMESTAMP 
                    WHERE user_id = ?
                ''', (user_id,))
                conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Ошибка обновления активности пользователя: {e}")

    def add_practice_session(self, user_id: int, phrase_id: str, user_response: str, is_correct: bool):
        """Добавление записи о сессии практики."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO practice_sessions (user_id, phrase_id, user_response, is_correct)
                    VALUES (?, ?, ?, ?)
                ''', (user_id, phrase_id, user_response, is_correct))
                conn.commit()
                return cursor.lastrowid
        except sqlite3.Error as e:
            logger.error(f"Ошибка добавления сессии практики: {e}")
            return None

    def add_support_request(self, user_id: int, question: str, response: str = None,
                            is_escalated: bool = False, operator_id: int = None):
        """Добавление запроса поддержки."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO support_requests (user_id, question, response, is_escalated, operator_id)
                    VALUES (?, ?, ?, ?, ?)
                ''', (user_id, question, response, is_escalated, operator_id))
                conn.commit()
                return cursor.lastrowid
        except sqlite3.Error as e:
            logger.error(f"Ошибка добавления запроса поддержки: {e}")
            return None

    def log_error(self, user_id: int, error_message: str, stack_trace: str = None):
        """Логирование ошибки."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO error_logs (user_id, error_message, stack_trace)
                    VALUES (?, ?, ?)
                ''', (user_id, error_message, stack_trace))
                conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Ошибка логирования ошибки: {e}")


# Создаем глобальный экземпляр базы данных
db = Database()
        