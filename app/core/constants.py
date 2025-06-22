"""Модуль для создания констант."""

from typing import Final

CATEGORY_NAME_MAX_LENGTH: Final = 64

PRODUCT_NAME_MAX_LENGTH: Final = 64
PRODUCT_IMAGE_URL_MAX_LENGTH: Final = 128

SLUG_REGEXP: Final = r'^[a-z0-9\-]{1,64}$'

USER_FIRST_NAME_MAX_LENGTH: Final = 64
USER_LAST_NAME_MAX_LENGTH: Final = 64
USER_EMAIL_MAX_LENGTH: Final = 64
USER_PASSWORD_MAX_LENGTH: Final = 64
USER_USERNAME_REGEXP: Final = r'^[\w.\-]{1,64}$'
