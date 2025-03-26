"""Модуль для создания исключений."""

from fastapi import HTTPException, status


class NotFound(HTTPException):
    """Исключение с ошибкой 404."""

    def __init__(self, detail: str | None = None) -> None:
        """Магический метод для инициализации атрибутов объекта."""
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class Forbidden(HTTPException):
    """Исключение с ошибкой 403."""

    def __init__(self, detail: str | None = None) -> None:
        """Магический метод для инициализации атрибутов объекта."""
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


class ValidationError(HTTPException):
    """Исключение с ошибкой 400."""

    def __init__(self, detail: str | None = None) -> None:
        """Магический метод для инициализации атрибутов объекта."""
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST,
                         detail=detail)
