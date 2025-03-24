"""Модуль для создания генератора сессий."""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import async_session_maker


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Функция для создания сессий."""
    async with async_session_maker() as session:
        yield session
