from app.core.db import Base
from sqlalchemy import text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import RoleEnum


class User(Base):
    __tablename__ = 'users'

    first_name: Mapped[str]
    last_name: Mapped[str]
    username: Mapped[str] = mapped_column(unique=True)
    email: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    role: Mapped[RoleEnum] = mapped_column(
        default=RoleEnum.IS_CUSTOMER,
        server_default=text("'IS_CUSTOMER'")
    )

    products = relationship('Product', back_populates='user')
    reviews = relationship('Review', back_populates='user')
