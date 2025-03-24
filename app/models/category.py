"""Модуль для создания моделей БД."""

from sqlalchemy import ForeignKey, String, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.constants import CATEGORY_NAME_MAX_LENGTH, SLUG_REGEXP
from app.core.db import Base


class Category(Base):
    """Модель Category."""

    __tablename__ = 'categories'
    __table_args__ = (
        CheckConstraint('parent_id > 0', name='parent_id_natural_constraint'),
        CheckConstraint(f'slug ~ "{SLUG_REGEXP}"',
                        name='slug_regexp_constraint')
    )

    name: Mapped[str] = mapped_column(String(CATEGORY_NAME_MAX_LENGTH))
    slug: Mapped[str] = mapped_column(unique=True, index=True)
    parent_id: Mapped[int | None] = mapped_column(ForeignKey('categories.id'),
                                                  default=None,)

    products = relationship('Product', back_populates='category')
