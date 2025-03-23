from app.models.category import Category
from app.models.product import Product
from app.models.review import Review


CATEGORY_NAME_MAX_LENGTH = 64

PRODUCT_NAME_MAX_LENGTH = 64
PRODUCT_DESCRIPTION_MAX_LENGTH = 256
PRODUCT_IMAGE_URL_MAX_LENGTH = 128

REVIEW_TEXT_MAX_LENGTH = 256

USER_FIRST_NAME_MAX_LENGTH = 64
USER_LAST_NAME_MAX_LENGTH = 64
USER_EMAIL_MAX_LENGTH = 64
USER_PASSWORD_MAX_LENGTH = 64
USER_USERNAME_PATTERN = r'^[\w.-$]{0,32}$'

CATEGORY_DATA = (Category.id,
                 Category.name,
                 Category.slug,
                 Category.parent_id)

PRODUCT_DATA = (Product.id,
                Product.name,
                Product.slug,
                Product.description,
                Product.price,
                Product.image_url,
                Product.stock,
                Product.rating)

REVIEW_DATA = (Review.id,
               Review.grade,
               Review.text,
               Review.user_id,
               Review.product_id)
