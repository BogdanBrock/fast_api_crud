from pydantic import BaseModel, Field, computed_field
from slugify import slugify

from app.core.constants import CATEGORY_NAME_MAX_LENGTH


class CategorySchema(BaseModel):
    name: str = Field(max_length=CATEGORY_NAME_MAX_LENGTH)
    parent_id: int | None = Field(ge=1, default=None)

    @computed_field
    def slug(self) -> str:
        return slugify(self.name)
