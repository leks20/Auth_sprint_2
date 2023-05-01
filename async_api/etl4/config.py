from typing import Any

from pydantic import BaseSettings


class Settings(BaseSettings):
    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_PORT: int

    DEFAULT_DATE: Any
    PAGE_SIZE: int
    PATH_TO_STATE: str
    ES_URL: str

    class Config:
        env_file = "./.env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()
