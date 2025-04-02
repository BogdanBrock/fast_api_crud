"""Модуль создания разрешений для пользователя."""

from typing import TypedDict

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.endpoints.user import get_current_user
from app.api.exceptions import ForbiddenError
from app.api.validators import (get_product_or_not_found,
                                get_review_or_not_found)
from app.core.db import db_session
from app.crud import ModelType
from app.models import Product, Review, RoleEnum, User


class RequestContext(TypedDict):
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
        await self.not_has_permission(user)
        context = {'user': user, 'session': session}
        if not (data := request.path_params):
            return RequestContext(context)
        model_obj = await self.get_object(data, session)
        await self.not_has_object_permission(user, model_obj)
        context['model_obj'] = model_obj
        return RequestContext(context)

    async def not_has_permission(self, user: User) -> None:
        """Разрешение на уровне запроса."""
        if user.role not in self.allowed_roles:
            raise ForbiddenError('Недостаточно прав для этого действия.')

    @staticmethod
    async def not_has_object_permission(user: User, obj: ModelType) -> None:
        """Разрешение на уровне объекта."""
        if not (user.role == RoleEnum.IS_ADMIN or
                user.username == obj.user_username):
            raise ForbiddenError('Нельзя изменять или удалять чужие данные.')


class IsAdminPermission(BasePermission):
    """Разрешение для администратора."""

    def __init__(self):
        """Магический метод для инициализации объекта."""
        super().__init__(RoleEnum.IS_ADMIN)


class IsSupplierOrAdminPermission(BasePermission):
    """Разрешение для поставщика или же для администратора."""

    def __init__(self) -> None:
        """Магический метод для инициализации объекта."""
        super().__init__(RoleEnum.IS_SUPPLIER,
                         RoleEnum.IS_ADMIN)


class IsSupplierOwnerOrAdminPermission(IsSupplierOrAdminPermission):
    """Разрешение для владельца продукта или же для администратора."""

    @staticmethod
    async def get_object(data: dict, session: AsyncSession) -> Product:
        """Метод для получения объекта модели Product."""
        product_slug = data.get('product_slug')
        return await get_product_or_not_found(product_slug, session)


class IsOwnerOrAdminPermission(BasePermission):
    """Разрешение для владельца отзыва или же для администратора."""

    def __init__(self) -> None:
        """Магический метод для инициализации объекта."""
        super().__init__(RoleEnum.IS_CUSTOMER,
                         RoleEnum.IS_SUPPLIER,
                         RoleEnum.IS_ADMIN)

    @staticmethod
    async def get_object(data: dict, session: AsyncSession) -> Review:
        """Метод для получения объекта модели Review."""
        product_slug = data.get('product_slug')
        await get_product_or_not_found(product_slug, session)
        review_id = data.get('review_id')
        return await get_review_or_not_found(review_id, session)


is_admin_permission = IsAdminPermission()
is_supplier_or_admin_permission = IsSupplierOrAdminPermission()
is_supplier_owner_or_admin_permission = IsSupplierOwnerOrAdminPermission()
is_owner_or_admin_permission = IsOwnerOrAdminPermission()
