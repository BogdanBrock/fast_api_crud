from enum import Enum

from app.backend.db import Base
from sqlalchemy import text
from sqlalchemy.orm import Mapped, mapped_column, relationship


class RoleEnum(str, Enum):
    IS_ADMIN = 'администратор'
    IS_SUPPLIER = 'поставщик'
    IS_CUSTOMER = 'покупатель'


class User(Base):
    __tablename__ = 'users'

    first_name: Mapped[str]
    last_name: Mapped[str]
    username: Mapped[str] = mapped_column(unique=True)
    email: Mapped[str] = mapped_column(unique=True)
    hashed_password: Mapped[str]
    role: Mapped[RoleEnum] = mapped_column(
        default=RoleEnum.IS_CUSTOMER,
        server_default=text("'IS_CUSTOMER'")
    )
    products = relationship('Product', back_populates='user')
    reviews = relationship('Review', back_populates='user')
