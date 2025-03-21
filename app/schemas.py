from pydantic import BaseModel, EmailStr, Field

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


class CategorySchema(BaseModel):
    name: str
    parent_id: int | None = None


class ReviewSchema(BaseModel):
    text: str | None = None
    grade: int = Field(ge=0, le=10)
