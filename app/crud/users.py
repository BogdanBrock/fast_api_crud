"""Модуль для создания CRUD операций для пользователя."""

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models import User


class CRUDUser(CRUDBase):
    """Класс для создания CRUD операций для пользователя."""

    async def get_user_by_username(
        self,
        username: str,
        session: AsyncSession
    ) -> User | None:
        """Метод для получения пользователя по имени пользователя."""
        user = await session.execute(
            select(User).
            where(User.username == username)
        )
        return user.scalar()

    async def get_username_and_email(
        self,
        username: str,
        email: str,
        session: AsyncSession
    ) -> tuple[str, str] | None:
        """Метод для получения имени пользователя и почты."""
        user = await session.execute(
            select(User.username, User.email).
            where(or_(User.username == username,
                      User.email == email))
        )
        return user.mappings().first()


user_crud = CRUDUser(User)
