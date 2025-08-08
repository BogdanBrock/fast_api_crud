"""Модуль создания разрешений для пользователей."""

from typing import TypedDict

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ForbiddenError
from app.core.db import db_session
from app.core.security import get_current_user
from app.core.validators import (
    get_category_or_not_found,
    get_product_or_not_found,
    get_review_or_not_found
)
from app.crud import ModelType
from app.models import Product, Review, RoleEnum, User


class RequestContext(TypedDict):
    """Контекст запроса."""

    user: User
    session: AsyncSession
    model_obj: ModelType = None


class BasePermission:
    """Базовый класс для разрешений."""

    def __init__(self, *allowed_roles: tuple[RoleEnum, ...]):
        """Магический метод для инициализации объекта."""
        self.allowed_roles = allowed_roles

    async def __call__(
        self,
        request: Request,
        session: AsyncSession = Depends(db_session),
        user: User = Depends(get_current_user)
    ) -> RequestContext:
        """Магический метод для вызова функции."""
        if request.method == 'POST' and await self.has_permission(user):
            return RequestContext(user=user, session=session)
        model_obj = await self.get_object(request.path_params, session)
        await self.has_object_permission(user, model_obj)
        return RequestContext(user=user, session=session, model_obj=model_obj)

    async def has_permission(self, user: User) -> True:
        """Разрешение на уровне запроса."""
        if user.role not in self.allowed_roles:
            raise ForbiddenError('Недостаточно прав для этого действия.')
        return True

    @staticmethod
    async def has_object_permission(user: User, obj: ModelType) -> True:
        """Разрешение на уровне объекта."""
        if not (user.role == RoleEnum.ADMIN or
                user.username == obj.user_username):
            raise ForbiddenError('Нельзя изменять или удалять чужие данные.')
        return True

    @staticmethod
    async def get_object(params: dict, session: AsyncSession) -> ModelType:
        """Метод для получения объекта модели."""


class IsAdminPermission(BasePermission):
    """Разрешение для администратора."""

    def __init__(self):
        """Магический метод для инициализации объекта."""
        super().__init__(RoleEnum.ADMIN)

    @staticmethod
    async def get_object(params: dict, session: AsyncSession) -> ModelType:
        """Метод для получения объекта модели категории."""
        category_slug = params.get('category_slug')
        return await get_category_or_not_found(category_slug, session)

    @staticmethod
    async def has_object_permission(user: User, obj: ModelType) -> True:
        """Разрешение на уровне объекта."""
        if not user.role == RoleEnum.ADMIN:
            raise ForbiddenError(
                'Только администратору можно изменять или удалять данные.'
            )
        return True


class IsSupplierOrAdminPermission(BasePermission):
    """Разрешение для поставщика или же для администратора."""

    def __init__(self) -> None:
        """Магический метод для инициализации объекта."""
        super().__init__(RoleEnum.SUPPLIER,
                         RoleEnum.ADMIN)


class IsSupplierOwnerOrAdminPermission(IsSupplierOrAdminPermission):
    """Разрешение для владельца продукта или же для администратора."""

    @staticmethod
    async def get_object(params: dict, session: AsyncSession) -> Product:
        """Метод для получения объекта модели продукта."""
        product_slug = params.get('product_slug')
        return await get_product_or_not_found(product_slug, session)


class IsOwnerOrAdminPermission(BasePermission):
    """Разрешение для владельца отзыва или же для администратора."""

    def __init__(self) -> None:
        """Магический метод для инициализации объекта."""
        super().__init__(RoleEnum.CUSTOMER,
                         RoleEnum.SUPPLIER,
                         RoleEnum.ADMIN)

    @staticmethod
    async def get_object(params: dict, session: AsyncSession) -> Review:
        """Метод для получения объекта модели отзыва."""
        product_slug = params.get('product_slug')
        await get_product_or_not_found(product_slug, session)
        review_id = params.get('review_id')
        return await get_review_or_not_found(int(review_id), session)


is_admin_permission = IsAdminPermission()
is_supplier_or_admin_permission = IsSupplierOrAdminPermission()
is_supplier_owner_or_admin_permission = IsSupplierOwnerOrAdminPermission()
is_owner_or_admin_permission = IsOwnerOrAdminPermission()
