"""Модуль для создания схем модели Product."""


from pydantic import BaseModel, Field, HttpUrl, field_validator

from app.core.constants import (PRODUCT_IMAGE_URL_MAX_LENGTH,
                                PRODUCT_NAME_MAX_LENGTH)
from app.schemas import AbstractBaseSchema


class ProductUpdateSchema(AbstractBaseSchema):
    """Схема ProductUpdateSchema для валидации и обновления данных."""
    name: str = Field(max_length=PRODUCT_NAME_MAX_LENGTH, default=None)
    description: str | None = None
    image_url: HttpUrl | None = Field(max_length=PRODUCT_IMAGE_URL_MAX_LENGTH,
                                      default=None)
    price: float = Field(gt=0, default=None)
    stock: int = Field(ge=0, default=None)

    @field_validator('image_url', mode='after')
    @classmethod
    def validate_image_url(cls, value) -> str:
        """Метод для преобразования поля image_url в строку."""
        return str(value)

    def model_dump(self, *args, **kwargs):
        """Метод для создания словаря из модели pydantic."""
        update_data = super().model_dump(*args, **kwargs)
        if 'name' not in update_data:
            del update_data['slug']
        return update_data


class ProductCreateSchema(ProductUpdateSchema):
    """Схема ProductCreateSchema для валидации и создания данных."""

    name: str = Field(max_length=PRODUCT_NAME_MAX_LENGTH)
    price: float = Field(gt=0)
    stock: int = Field(ge=0)
    category_slug: str


class ProductReadSchema(BaseModel):
    """Схема ProductReadSchema для чтения данных."""

    id: int
    name: str
    slug: str
    description: str | None
    image_url: HttpUrl | None
    price: int
    stock: int
    category_slug: str
    user_username: str
    rating: float | None
