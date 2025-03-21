from fastapi import HTTPException, status


async def get_object_or_404(session, query):
    obj = await session.scalar(query)
    if not obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'{query.__name__} не найден.'
        )
    return obj
