"""Модуль для создания ограниченного набора именованных значения."""

from enum import Enum


class RoleEnum(str, Enum):
    """Класс RoleEnum для определения роли пользователя."""

    IS_CUSTOMER = 'Покупатель'
    IS_SUPPLIER = 'Поставщик'
    IS_ADMIN = 'Администратор'
