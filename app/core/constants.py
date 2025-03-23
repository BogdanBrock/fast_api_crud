from app.models.categories import Category
from app.models.products import Product
from app.models.reviews import Review

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
