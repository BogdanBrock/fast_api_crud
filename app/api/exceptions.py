"""Модуль для создания валидаторов."""

from fastapi import HTTPException, status


class ValidationError(HTTPException):
    """Исключение ValidationError."""

    def __init__(self, detail: str | None = None):
        """Магический метод для инициализации атрибутов объекта."""
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST,
                         detail=detail)


class UnauthorizedError(HTTPException):
    """Исключение UnauthorizedError."""

    def __init__(self, detail: str | None = None):
        """Магический метод для инициализации атрибутов объекта."""
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED,
                         detail=detail)


class ForbiddenError(HTTPException):
    """Исключение ForbiddenError."""

    def __init__(self, detail: str | None = None):
        """Магический метод для инициализации атрибутов объекта."""
        super().__init__(status_code=status.HTTP_403_FORBIDDEN,
                         detail=detail)


class NotFoundError(HTTPException):
    """Исключение NotFoundError."""

    def __init__(self, detail: str | None = None):
        """Магический метод для инициализации атрибутов объекта."""
        super().__init__(status_code=status.HTTP_404_NOT_FOUND,
                         detail=detail)
