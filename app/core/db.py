"""Модуль для создания базовой модели и фабрики сессий."""

from datetime import datetime
from typing import AsyncGenerator

from sqlalchemy import func
from sqlalchemy.ext.asyncio import (
    AsyncAttrs,
    AsyncSession,
    async_sessionmaker,
    create_async_engine
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from app.core.config import settings

engine = create_async_engine(settings.db_url, echo=True)

async_session_maker = async_sessionmaker(
    engine,
    expire_on_commit=False,
    class_=AsyncSession
)


async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Функция для создания сессий."""
    async with async_session_maker() as session:
        yield session


class Base(AsyncAttrs, DeclarativeBase):
    """Базовая модель Base."""

    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        onupdate=func.now()
    )
