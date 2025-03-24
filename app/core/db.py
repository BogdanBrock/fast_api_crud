"""Модуль для создания базовой модели и фабрики сессий."""

from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import (
    create_async_engine, async_sessionmaker, AsyncSession, AsyncAttrs
)

from app.config import settings

engine = create_async_engine(settings.db_url, echo=True)
async_session_maker = async_sessionmaker(engine,
                                         expire_on_commit=False,
                                         class_=AsyncSession)


class Base(AsyncAttrs, DeclarativeBase):
    """Базовая модель Base."""

    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(),
                                                 onupdate=func.now())
