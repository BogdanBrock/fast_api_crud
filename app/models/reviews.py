from sqlalchemy import Column, Integer, Text

from app.backend.db import Base


class Review(Base):
    __tablename__ = 'reviews'

    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text, nullable=False)
