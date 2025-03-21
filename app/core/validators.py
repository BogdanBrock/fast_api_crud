from fastapi import HTTPException, status


async def validate_owner(obj, user):
    if obj.user.username != user.get('username'):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f'Только владелец может изменить {obj.__name__}.'
        )


async def validate_owner_cant_rate_own_product(obj, user):
    if obj.user.username == user.get('username'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Нельзя оставить отзыв на свой товар.'
        )
