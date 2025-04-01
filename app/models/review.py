"""Модуль для создания модели Review."""

from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base


class Review(Base):
    """Модель Review."""

    __tablename__ = 'reviews'

    grade: Mapped[int]
    text: Mapped[str | None] = mapped_column(Text, default=None)
    user_username: Mapped[int] = mapped_column(ForeignKey('users.username'))
    product_slug: Mapped[int] = mapped_column(ForeignKey('products.slug'))

    user: Mapped['User'] = relationship(
        'User',
        back_populates='reviews'
    )
    product: Mapped['Product'] = relationship(
        'Product',
        back_populates='reviews'
    )
