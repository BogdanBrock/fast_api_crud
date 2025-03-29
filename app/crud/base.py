"""Модуль для создания базовых CRUD операций."""

from typing import TypeVar, Generic

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.core.db import Base
from app.models import User

ModelType = TypeVar('ModelType', bound=Base)
SchemaType = TypeVar('Schematype', bound=BaseModel)


class CRUDBase(Generic[ModelType, SchemaType]):
    """Класс для создания базовых CRUD операций."""

    def __init__(self, model):
        """Магический метод для инициализации атрибутов объекта."""
        self.model = model

    async def get_all(
        self,
        session: AsyncSession
    ) -> list[ModelType]:
        """Метод для получения всех объектов."""
        objs = await session.execute(select(self.model))
        return objs.scalars().all()

    async def get(
        self,
        id: int,
        session: AsyncSession
    ) -> ModelType | None:
        """Метод для получения объекта."""
        obj = await session.execute(
            select(self.model).
            where(self.model.id == id)
        )
        return obj.scalar()

    async def create(
        self,
        schema: SchemaType,
        session: AsyncSession,
        user: User = None
    ) -> ModelType:
        """Метод для создания объекта."""
        schema_data = schema.model_dump()
        if user:
            schema_data['user_id'] = user.id
        model_obj = self.model(**schema_data)
        session.add(model_obj)
        await session.commit()
        await session.refresh(model_obj)
        return model_obj

    async def update(
        self,
        model_obj: ModelType,
        schema: SchemaType,
        session: AsyncSession
    ) -> ModelType:
        """Метод для изменения объекта."""
        update_data = schema.model_dump()
        for key in update_data:
            setattr(model_obj, key, update_data[key])
        await session.commit()
        await session.refresh(model_obj)
        return model_obj

    async def delete(
        self,
        model_obj: ModelType,
        session: AsyncSession
    ) -> None:
        """Метод для удаления объекта."""
        await session.delete(model_obj)
        await session.commit()


class AbstractCRUDBase(CRUDBase):
    """Абстрактный класс для наследования."""

    async def get_object_by_slug(
        self,
        slug: str,
        session: AsyncSession
    ) -> ModelType | None:
        """Метод для получения объекта по slug."""
        obj = await session.execute(
            select(self.model).
            where(self.model.slug == slug)
        )
        return obj.scalar()
