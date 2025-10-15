from datetime import datetime
import json
import os
from typing import Any, Dict

class UserData:
    def __init__(self, file_path: str = "users.json"):
        self.file_path = file_path
        # os.makedirs(os.path.dirname(file_path), exist_ok=True)
        if not os.path.exists(file_path):
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump({}, f, ensure_ascii=False, indent=4)

    def _read(self) -> Dict[str, Any]:
        """Читает JSON-файл и возвращает словарь"""
        with open(self.file_path, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}

    def _write(self, data: Dict[str, Any]) -> None:
        """Сохраняет словарь в JSON"""
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def add_user(self, user_id: int, FIO: str) -> None:
        """Добавляет нового пользователя или обновляет существующего"""
        data = self._read()

        data[str(user_id)] = {
            "FIO": FIO,
            "joined_at": datetime.now().isoformat(timespec="seconds")
        }

        self._write(data)

    def get_user(self, user_id: int) -> Dict[str, Any] | None:
        """Возвращает данные пользователя по ID"""
        data = self._read()
        return data.get(str(user_id), None)

    def all_users(self) -> Dict[str, Any]:
        """Возвращает всех пользователей"""
        return self._read()

    def remove_user(self, user_id: int) -> None:
        """Удаляет пользователя"""
        data = self._read()
        if str(user_id) in data:
            del data[str(user_id)]
            self._write(data)