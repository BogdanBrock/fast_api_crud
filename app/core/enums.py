"""Модуль для создания ограниченного набора именованных значения."""

from enum import Enum


class RoleEnum(str, Enum):
    """Класс RoleEnum для определения роли пользователя."""

    IS_CUSTOMER = 'покупатель'
    IS_SUPPLIER = 'поставщик'
    IS_ADMIN = 'администратор'
