from fastapi import Depends, HTTPException, status

from app.core.enums import RoleEnum
from app.routers.auth import get_current_user


class RoleChecker:
    def __init__(self, allowed_roles: tuple[str]) -> None:
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: dict = Depends(get_current_user)) -> True:
        if current_user.get('role') in self.allowed_roles:
            return True
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
