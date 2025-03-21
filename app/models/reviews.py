from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base


class Review(Base):
    __tablename__ = 'reviews'

    grade: Mapped[int]
    text: Mapped[str | None] = mapped_column(Text, default=None)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    product_id: Mapped[int] = mapped_column(ForeignKey('products.id'))

    user = relationship('User', back_populates='reviews')
    product = relationship('Product', back_populates='reviews')
