"""Модуль создания разрешений для пользователя."""

from fastapi import Depends, HTTPException, status

from app.core.enums import RoleEnum
from app.routers.auth import get_current_user


class RoleChecker:
    """Класс для создания разрешений."""

    def __init__(self, allowed_roles: tuple[str]) -> None:
        """Магический метод для инициализации атрибутов."""
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: dict = Depends(get_current_user)) -> None:
        """Магический метод для определения прав пользователя."""
        if current_user.get('role') not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Вы не имеете прав для доступа.'
            )


is_admin_permission = Depends(
    RoleChecker((RoleEnum.IS_ADMIN))
)
is_admin_or_is_supplier_permission = Depends(
    RoleChecker((RoleEnum.IS_ADMIN,
                RoleEnum.IS_SUPPLIER))
)
