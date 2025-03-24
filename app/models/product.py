"""Модуль для создания моделей БД."""

from sqlalchemy import ForeignKey, select, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.hybrid import hybrid_property

from app.core.db import Base


class Product(Base):
    """Модель Product."""

    __tablename__ = 'products'

    name: Mapped[str]
    slug: Mapped[str] = mapped_column(unique=True, index=True)
    description: Mapped[str | None] = None
    price: Mapped[int]
    image_url: Mapped[str]
    stock: Mapped[int]
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    category_id: Mapped[int] = mapped_column(ForeignKey('categories.id'))

    category = relationship('Category', back_populates='products')
    user = relationship('User', back_populates='products')
    reviews = relationship('Review', back_populates='product')

    @hybrid_property
    def rating(self):
        """Функция для вычисления поля rating."""
        from app.models.review import Review

        return (select(func.round(func.avg(Review.grade), 1)).
                where(Review.product_id == Product.id).
                correlate(Product).
                scalar_subquery()
                )
