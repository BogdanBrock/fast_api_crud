"""Модуль для создания модели User."""

from enum import Enum

from sqlalchemy import String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.constants import (USER_FIRST_NAME_MAX_LENGTH,
                                USER_LAST_NAME_MAX_LENGTH,
                                USER_PASSWORD_MAX_LENGTH,
                                USER_EMAIL_MAX_LENGTH)
from app.core.db import Base


class RoleEnum(str, Enum):
    """Класс RoleEnum для определения роли пользователя."""

    IS_CUSTOMER = 'Покупатель'
    IS_SUPPLIER = 'Поставщик'
    IS_ADMIN = 'Администратор'


class User(Base):
    """Модель User."""

    __tablename__ = 'users'

    first_name: Mapped[str] = mapped_column(String(USER_FIRST_NAME_MAX_LENGTH))
    last_name: Mapped[str] = mapped_column(String(USER_LAST_NAME_MAX_LENGTH))
    username: Mapped[str] = mapped_column(unique=True, index=True)
    email: Mapped[str] = mapped_column(
        String(USER_EMAIL_MAX_LENGTH),
        unique=True
    )
    password: Mapped[str] = mapped_column(String(USER_PASSWORD_MAX_LENGTH))
    role: Mapped[RoleEnum] = mapped_column(
        default=RoleEnum.IS_CUSTOMER,
        server_default=text("'IS_CUSTOMER'")
    )

    products: Mapped[list['Product']] = relationship(
        'Product',
        back_populates='user',
        cascade='all, delete-orphan'
    )
    reviews: Mapped[list['Review']] = relationship(
        'Review',
        back_populates='user',
        cascade='all, delete-orphan'
    )
