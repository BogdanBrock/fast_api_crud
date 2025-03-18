from sqlalchemy import Column, Integer, ForeignKey, Text, func, Date
from sqlalchemy.orm import relationship

from app.backend.db import Base


class Review(Base):
    __tablename__ = 'reviews'

    id = Column(Integer, primary_key=True, index=True)
    grade = Column(Integer, nullable=False)
    text = Column(Text)
    date = Column(Date, server_default=func.now())
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    user = relationship('User', back_populates='reviews')
    product = relationship('Product', back_populates='reviews')
