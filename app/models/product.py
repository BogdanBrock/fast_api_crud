"""Модуль для создания моделей БД."""

from sqlalchemy import ForeignKey, String, Text, Numeric, select, func
from sqlalchemy.orm import (Mapped, declared_attr, mapped_column,
                            relationship, column_property)

from app.core.constants import (PRODUCT_NAME_MAX_LENGTH,
                                PRODUCT_IMAGE_URL_MAX_LENGTH)
from app.core.db import Base
from app.models.review import Review


class Product(Base):
    """Модель Product."""

    __tablename__ = 'products'

    name: Mapped[str] = mapped_column(String(PRODUCT_NAME_MAX_LENGTH))
    slug: Mapped[str] = mapped_column(unique=True, index=True)
    description: Mapped[str | None] = mapped_column(Text, default=None)
    price: Mapped[float]
    image_url: Mapped[str] = mapped_column(
        String(PRODUCT_IMAGE_URL_MAX_LENGTH)
    )
    stock: Mapped[int]
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    category_id: Mapped[int] = mapped_column(ForeignKey('categories.id'))

    category = relationship('Category', back_populates='products')
    user = relationship('User', back_populates='products')
    reviews = relationship('Review', back_populates='product')

    @declared_attr
    def rating(cls):
        return column_property(
            select(func.avg(Review.grade)).
            where(Review.product_id == cls.id).
            scalar_subquery().
            cast(Numeric(3, 1))
        )
