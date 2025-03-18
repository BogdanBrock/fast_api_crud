from pydantic import BaseModel, Field


class ProductSchema(BaseModel):
    name: str
    description: str
    price: int
    image_url: str
    stock: int
    category: int


class CategorySchema(BaseModel):
    name: str
    parent_id: int | None = None


class UserSchema(BaseModel):
    first_name: str
    last_name: str
    username: str
    email: str
    password: str


class ReviewSchema(BaseModel):
    text: str | None = None
    grade: int = Field(ge=0, le=10)
