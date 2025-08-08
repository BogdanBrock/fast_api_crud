"""Модуль для создания валидаторов."""

from fastapi import HTTPException, status


class ValidationError(HTTPException):
    """Ошибка 400 для валидации данных."""

    def __init__(self, detail: str | None = None):
        """Магический метод для инициализации атрибутов объекта."""
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST,
                         detail=detail)


class UnauthorizedError(HTTPException):
    """Ошибка 401 для ограничения прав анонимных пользователей."""

    def __init__(self, detail: str | None = None):
        """Магический метод для инициализации атрибутов объекта."""
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED,
                         detail=detail)


class ForbiddenError(HTTPException):
    """Ошибка 403 для ограничения прав авторизованных пользователей."""

    def __init__(self, detail: str | None = None):
        """Магический метод для инициализации атрибутов объекта."""
        super().__init__(status_code=status.HTTP_403_FORBIDDEN,
                         detail=detail)


class NotFoundError(HTTPException):
    """Ошибка 404 в случае отсутствия объекта."""

    def __init__(self, detail: str | None = None):
        """Магический метод для инициализации атрибутов объекта."""
        super().__init__(status_code=status.HTTP_404_NOT_FOUND,
                         detail=detail)
