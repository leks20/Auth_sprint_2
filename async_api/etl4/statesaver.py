import abc
import json
from typing import Any


class BaseStorage:
    @abc.abstractmethod
    def save_state(self, state: dict) -> None:
        """Сохранить состояние в постоянное хранилище"""
        pass

    @abc.abstractmethod
    def retrieve_state(self) -> dict:
        """Загрузить состояние локально из постоянного хранилища"""
        pass


class JsonFileStorage(BaseStorage):
    def __init__(self, file_path: str | None = None):
        self.file_path = file_path

    def save_state(self, state):
        with open(self.file_path, "w") as write_file:
            json.dump(state, write_file)

    def retrieve_state(self):
        try:
            with open(self.file_path, "r") as read_file:
                return json.load(read_file)
        except Exception:
            return {}


class State:
    """
    Класс для хранения состояния при работе с данными, чтобы постоянно не перечитывать данные с начала.
    Здесь представлена реализация с сохранением состояния в файл.
    В целом ничего не мешает поменять это поведение на работу с БД или распределённым хранилищем.
    """

    def __init__(self, storage: BaseStorage):
        self.storage = storage

    def set_state(self, key: str, value: Any) -> None:
        state = self.storage.retrieve_state()
        state[key] = value
        self.storage.save_state(state)

    def get_state(self, key: str) -> Any:
        state = self.storage.retrieve_state()
        if key in state:
            return state.get(key)
        else:
            return None
