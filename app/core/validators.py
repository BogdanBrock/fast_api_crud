"""Модуль для создания валидаторов."""

from app.core.exceptions import NotFoundError, ValidationError
from app.core.db import AsyncSession
from app.crud import category_crud, product_crud, review_crud, user_crud
from app.crud import ModelType
from app.models import Category, Product, Review


async def get_category_or_not_found(
    category_slug: str,
    session: AsyncSession,
) -> Category | None:
    """Валидация существования категории и получения категории."""
    category = await category_crud.get_object_by_slug(category_slug, session)
    if not category:
        raise NotFoundError('Такой категории не существует.')
    return category


async def check_category_already_exists(
    category_slug: str,
    session: AsyncSession
) -> Category | None:
    """Валидация уже существующей категории."""
    category = await category_crud.get_object_by_slug(category_slug, session)
    if category:
        raise ValidationError('Уже есть такая категория.')


async def check_cant_change_parent_category(
    category_slug: str,
    session: AsyncSession,
) -> None:
    """Валидация для невозможности изменения родительскогой категории."""
    parent_slug = await category_crud.get_parent_slug(category_slug, session)
    if parent_slug:
        raise ValidationError('Нельзя поменять родительскую категорию.')


async def get_product_or_not_found(
    product_slug: str,
    session: AsyncSession
) -> Product | None:
    """Валидация существования продукта и получения продукта."""
    product = await product_crud.get_object_by_slug(product_slug, session)
    if not product:
        raise NotFoundError('Такого продукта не существует.')
    return product


async def check_product_already_exists(
    product_slug: str,
    session: AsyncSession
) -> Product | None:
    """Валидация уже существующего продукта."""
    product = await product_crud.get_object_by_slug(product_slug, session)
    if product:
        raise ValidationError('Уже есть такой продукт.')


async def get_review_or_not_found(
    review_id: int,
    session: AsyncSession
) -> Review | None:
    """Валидация существования отзыва и получения отзыва."""
    review = await review_crud.get(review_id, session)
    if not review:
        raise NotFoundError('Такого отзыва не существует.')
    return review


async def check_review_already_exists(
    product_slug: str,
    username: str,
    session: AsyncSession
) -> Review | None:
    """Валидация для уже существующего отзыва."""
    review = await review_crud.get_review_by_product_slug_and_username(
        product_slug,
        username,
        session
    )
    if review:
        raise ValidationError('Вы уже оставили отзыв на этот продукт.')


async def check_cant_review_own_product(
    current_username: str,
    review_username: ModelType
) -> None:
    """
    Валидация для проверки, что нельзя оценивать свой собственный продукт.
    """
    if current_username == review_username:
        raise ValidationError('Нельзя оставлять отзыв на свой продукт')


async def check_user_already_exists(
    username: str,
    email: str,
    session: AsyncSession
) -> None:
    """Валидация для уже существующего пользователя."""
    data = await user_crud.get_username_and_email(username, email, session)
    if data and username == data.get('username'):
        raise ValidationError('Такое имя пользователя уже существует.')
    if data and email == data.get('email'):
        raise ValidationError('Такая почта уже существует.')
