"""Модуль создания разрешений для пользователя."""

from fastapi import Depends

from app.api.exceptions import ForbiddenError
from app.core.enums import RoleEnum
from app.models import User
from app.api.endpoints.user import get_current_user


class BasePermission:
    """Базовый класс для создания разрешений."""

    def __init__(self, allowed_roles: tuple[RoleEnum, ...]):
        """Магический метод для инициализации атрибутов объекта."""
        self.allowed_roles = allowed_roles

    def __call__(self, user: User = Depends(get_current_user)) -> User | None:
        """Магический метод для вызова класса."""
        if user.role not in self.allowed_roles:
            raise ForbiddenError('Не достаточно прав для запроса.')
        return user


is_admin_permission = BasePermission((RoleEnum.IS_ADMIN,))
is_admin_or_supplier_permission = BasePermission((RoleEnum.IS_ADMIN,
                                                  RoleEnum.IS_SUPPLIER))


async def check_permission_for_user(user, obj_user) -> None:
    """Разрешение для изменения или удаления только своих данных."""
    if not (user.role == RoleEnum.IS_ADMIN or user == obj_user):
        raise ForbiddenError('Нельзя изменять или удалять чужие данные.')
