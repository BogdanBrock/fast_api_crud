"""Модуль для создания констант."""

CATEGORY_NAME_MAX_LENGTH = 64

PRODUCT_NAME_MAX_LENGTH = 64
PRODUCT_IMAGE_URL_MAX_LENGTH = 128

USER_FIRST_NAME_MAX_LENGTH = 64
USER_LAST_NAME_MAX_LENGTH = 64
USER_EMAIL_MAX_LENGTH = 64
USER_PASSWORD_MAX_LENGTH = 64

USERNAME_REGEXP = r'^[\w.\-]{0,64}$'
SLUG_REGEXP = r'^[a-z0-9\-]{0,64}$'


class ModelFields:
    """Класс для импорта полей моделей."""

    @property
    def CATEGORY_FIELDS(self):
        """Атрибут для получения полей категории."""
        from app.models import Category
        return (Category.id,
                Category.name,
                Category.slug,
                Category.parent_id)

    @property
    def PRODUCT_FIELDS(self):
        """Атрибут для получения полей продукта."""
        from app.models import Product
        return (Product.id,
                Product.name,
                Product.slug,
                Product.description,
                Product.price,
                Product.image_url,
                Product.stock,
                Product.rating)

    @property
    def REVIEW_FIELDS(self):
        """Атрибут для получения полей отзыва."""
        from app.models import Review
        return (Review.id,
                Review.grade,
                Review.text,
                Review.user_id,
                Review.product_id)


const = ModelFields()
