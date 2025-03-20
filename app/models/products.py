from sqlalchemy import ForeignKey, select, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.reviews import Review
from app.backend.db import Base
from app.backend.db_depends import get_db


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

    @property
    async def rating(self) -> int | None:
        session: AsyncSession = get_db()
        rating = await session.scalar(
            select(func.avg(Review.grade)).
            where(Product.id == Review.product_id)
        )
        return int(rating)

