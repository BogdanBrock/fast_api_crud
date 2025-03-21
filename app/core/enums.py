from enum import Enum


class RoleEnum(str, Enum):
    IS_CUSTOMER = 'покупатель'
    IS_SUPPLIER = 'поставщик'
    IS_ADMIN = 'администратор'
