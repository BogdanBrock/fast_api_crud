from sqlalchemy import Column, ForeignKey, Integer, String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.schema import CreateTable

from app.backend.db import Base
from app.models.products import Product


class Category(Base):
    __tablename__ = 'categories'

    name: Mapped[str]
    slug: Mapped[str] = mapped_column(unique=True, index=True)
    parend_id: Mapped[int | None] = mapped_column(ForeignKey('categories.id'),
                                                  default=None)
    products = relationship('Product', back_populates='category')
