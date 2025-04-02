"""Модуль для создания модели Product."""

from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric, String, Text, func, select
from sqlalchemy.orm import (Mapped, column_property, declared_attr,
                            mapped_column, relationship)
from sqlalchemy.ext.hybrid import hybrid_property

from app.core.constants import (PRODUCT_IMAGE_URL_MAX_LENGTH,
                                PRODUCT_NAME_MAX_LENGTH)
from app.core.db import Base


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
    user_username: Mapped[int] = mapped_column(ForeignKey('users.username'))
    category_slug: Mapped[int] = mapped_column(ForeignKey('categories.slug'))

    category: Mapped['Category'] = relationship(
        'Category',
        back_populates='products'
    )
    user: Mapped['User'] = relationship(
        'User',
        back_populates='products'
    )
    reviews: Mapped[list['Review']] = relationship(
        'Review',
        back_populates='product',
        cascade='all, delete-orphan'
    )

    @declared_attr
    def rating(cls) -> Decimal:
        """Атрибут для вычисления среднего рейтинга у продукта."""
        from app.models.review import Review
        return column_property(
            select(func.coalesce(func.avg(Review.grade), 0)).
            where(Review.product_slug == cls.slug).
            scalar_subquery().
            cast(Numeric(3, 1))
        )

    @hybrid_property
    def is_active(self) -> bool:
        """Атрибут показывающий наличие продукта."""
        return self.stock >= 1
