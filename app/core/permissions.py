"""Модуль создания разрешений для пользователя."""

from fastapi import Depends

from app.core.enums import RoleEnum
from app.core.exceptions import Forbidden
from app.models import User
from app.routers.auth import get_current_user


class BasePermission:
    """Базовый класс для создания разрешений."""

    def __init__(self, allowed_roles: tuple[str]) -> None:
        """Магический метод для инициализации атрибутов объекта."""
        self.allowed_roles = allowed_roles

    def __call__(self, user: User = Depends(get_current_user)) -> User | None:
        """Магический метод для вызова класса."""
        if user.role not in self.allowed_roles:
            raise Forbidden('Недостаточно прав для запроса.')
        return user


def has_object_permission(user, obj):
    if not (user.role == RoleEnum.IS_ADMIN or user == obj.user):
        raise Forbidden('Другой пользователь не может '
                        'изменять или удалять что-либо')


is_admin_permission = Depends(
    BasePermission((RoleEnum.IS_ADMIN,))
)
is_admin_or_supplier_permission = Depends(
    BasePermission((RoleEnum.IS_ADMIN,
                    RoleEnum.IS_SUPPLIER))
)
