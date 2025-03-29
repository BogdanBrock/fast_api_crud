"""Модуль для создания CRUD операций для пользователя."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models import User


class CRUDUser(CRUDBase):
    """Класс для созданий CRUD операций для пользователя."""

    async def get_user_by_username(
        self,
        username: str,
        session: AsyncSession
    ) -> User | None:
        user = await session.execute(
            select(User).
            where(User.username == username)
        )
        return user.scalar()


user_crud = CRUDUser(User)
