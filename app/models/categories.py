"""Модуль для создания модели Category."""

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.constants import CATEGORY_NAME_MAX_LENGTH
from app.core.db import Base


class Category(Base):
    """Модель Category."""

    __tablename__ = 'categories'
    __table_args__ = (
        UniqueConstraint('slug', name='unique_categories_slug'),
    )

    name: Mapped[str] = mapped_column(
        String(CATEGORY_NAME_MAX_LENGTH),
        unique=True
    )
    slug: Mapped[str] = mapped_column(unique=True, index=True)
    parent_slug: Mapped[str | None] = mapped_column(
        ForeignKey('categories.slug'),
        default=None
    )

    parent_category: Mapped['Category'] = relationship(
        'Category',
        lazy='selectin',
        back_populates='subcategories',
        remote_side='Category.slug'
    )
    subcategories: Mapped[list['Category']] = relationship(
        'Category',
        lazy='selectin',
        back_populates='parent_category',
        cascade='all, delete-orphan'
    )
    products: Mapped[list['Product']] = relationship(
        'Product',
        lazy='selectin',
        back_populates='category',
        cascade='all, delete-orphan'
    )
