"""Модуль для создания модели Review."""

from sqlalchemy import ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base


class Review(Base):
    """Модель Review."""

    __tablename__ = 'reviews'
    # __table_args__ = (UniqueConstraint('user_username', 'product_slug', name='unique_user_porudct'),)

    grade: Mapped[int]
    text: Mapped[str | None] = mapped_column(Text, default=None)
    user_username: Mapped[str] = mapped_column(ForeignKey('users.username'))
    product_slug: Mapped[str] = mapped_column(ForeignKey('products.slug'))

    user: Mapped['User'] = relationship(
        'User',
        lazy='selectin',
        back_populates='reviews'
    )
    product: Mapped['Product'] = relationship(
        'Product',
        lazy='selectin',
        back_populates='reviews'
    )
