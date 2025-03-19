from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.backend.db import Base


class Category(Base):
    __tablename__ = 'categories'

    name: Mapped[str]
    slug: Mapped[str] = mapped_column(unique=True, index=True)
    parend_id: Mapped[int | None] = mapped_column(ForeignKey('categories.id'),
                                                  default=None)
    products = relationship('Product', back_populates='category')
