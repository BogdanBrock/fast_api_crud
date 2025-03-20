from fastapi import Depends, HTTPException, status

from typing import Annotated

from app.routers.auth import get_current_user
from app.models.users import RoleEnum


async def is_supplier_or_is_admin_permission(
    user: Annotated[dict, Depends(get_current_user)]
):
    role = user.get('role')
    if not (role == RoleEnum.IS_SUPPLIER or role == RoleEnum.IS_ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Доступ есть только у поставщика и админа'
        )
    return user


async def is_admin_permission(
    user: Annotated[dict, Depends(get_current_user)]
):
    role = user.get('role')
    if role != RoleEnum.IS_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Доступ есть только у админа'
        )
