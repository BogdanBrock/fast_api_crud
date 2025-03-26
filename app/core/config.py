"""Модуль для настройки переменных окружения"""

import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Класс для настройки переменных окружения."""

    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    SECRET_KEY: str
    ALGORITHM: str

    model_config = SettingsConfigDict(
        env_file=os.path.join(
            os.path.dirname(os.path.dirname(__file__)), '.env'
        )
    )

    @property
    def db_url(self):
        """Получение пути для работы с БД."""
        return ('postgresql+asyncpg://'
                f'{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@'
                f'{self.DB_HOST}:{self.DB_PORT}/{self.POSTGRES_DB}')


settings = Settings()
