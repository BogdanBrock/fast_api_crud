from pydantic import BaseModel, EmailStr, Field, computed_field
from slugify import slugify

from app.core.enums import RoleEnum


class UserSchema(BaseModel):
    first_name: str
    last_name: str
    username: str
    email: EmailStr
    password: str
    role: RoleEnum = RoleEnum.IS_CUSTOMER


class ProductSchema(BaseModel):
    name: str
    description: str
    price: int
    image_url: str
    stock: int
    category_id: int

    @computed_field
    def slug(self) -> str:
        return slugify(self.name)


class CategorySchema(BaseModel):
    name: str
    parent_id: int | None = None

    @computed_field
    def slug(self) -> str:
        return slugify(self.name)


class ReviewSchema(BaseModel):
    text: str | None = None
    grade: int = Field(ge=0, le=10)
