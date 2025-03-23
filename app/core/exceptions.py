from fastapi import HTTPException, status


async def get_object_or_404(
    query, session, get_scalar=False, get_mapping=False
):
    if get_scalar:
        result = await session.scalar(query)
    elif get_mapping:
        result = (await session.execute(query)).mappings().first()
    else:
        raise ValueError('Необходимо указать get_scalar или get_mapping')
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Не найдено.'
        )
    return result
