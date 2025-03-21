from sqlalchemy import ForeignKey, select, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base
from app.models.reviews import Review


class Product(Base):
    __tablename__ = 'products'

    name: Mapped[str]
    slug: Mapped[str] = mapped_column(unique=True, index=True)
    description: Mapped[str | None] = None
    price: Mapped[int]
    image_url: Mapped[str]
    stock: Mapped[int]
    owner_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    category_id: Mapped[int] = mapped_column(ForeignKey('categories.id'))

    category = relationship('Category', back_populates='products')
    user = relationship('User', back_populates='products')
    reviews = relationship('Review', back_populates='product')

    async def get_rating(self, session):
        rating = await session.scalar(
            select(func.avg(Review.grade)).
            where(Review.product_id == Product.id)
        )
        return rating
