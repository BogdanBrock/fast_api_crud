from fastapi import Depends, HTTPException, status

from typing import Annotated

from app.routers.auth import get_current_user


async def is_supplier_or_is_admin_permission(
    user: Annotated[dict, Depends(get_current_user)]
):
    supplier_or_admin = any(
        [user.get(i) for i in ('is_supplier', 'is_admin')]
    )
    if not supplier_or_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Доступ есть только у продавца и админа'
        )
    return user


async def is_admin_permission(
    user: Annotated[dict, Depends(get_current_user)]
):
    admin = user.get('is_admin')
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Доступ есть только у админа'
        )
