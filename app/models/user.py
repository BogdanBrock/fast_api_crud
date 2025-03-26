"""Модуль для создания моделей БД."""

from sqlalchemy import CheckConstraint, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.constants import (USER_FIRST_NAME_MAX_LENGTH,
                                USER_LAST_NAME_MAX_LENGTH,
                                USER_PASSWORD_MAX_LENGTH,
                                USER_EMAIL_MAX_LENGTH,
                                USERNAME_REGEXP)
from app.core.db import Base
from app.core.enums import RoleEnum


class User(Base):
    """Модель User."""

    __tablename__ = 'users'
    __table_args__ = (
        CheckConstraint(f'username ~ "{USERNAME_REGEXP}"',
                        name='username_regexp_constraint'),
    )
    first_name: Mapped[str] = mapped_column(String(USER_FIRST_NAME_MAX_LENGTH))
    last_name: Mapped[str] = mapped_column(String(USER_LAST_NAME_MAX_LENGTH))
    username: Mapped[str] = mapped_column(unique=True)
    email: Mapped[str] = mapped_column(String(USER_EMAIL_MAX_LENGTH),
                                       unique=True)
    password: Mapped[str] = mapped_column(String(USER_PASSWORD_MAX_LENGTH))
    role: Mapped[RoleEnum] = mapped_column(
        default=RoleEnum.IS_CUSTOMER,
        server_default=text("'IS_CUSTOMER'")
    )

    products = relationship('Product', back_populates='user')
    reviews = relationship('Review', back_populates='user')
