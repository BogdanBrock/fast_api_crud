from app.models.categories import Category
from app.models.products import Product
from app.models.reviews import Review

SECRET_KEY = '6d97dfbc72b42506d9e109b58238f9accd67c6ccf25477dbcf76ba2a17d8d573'
ALGORITHM = 'HS256'
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
