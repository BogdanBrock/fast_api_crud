"""Модуль создания тестов для пользователей."""

from http import HTTPStatus
from typing import Any

import pytest
from httpx import AsyncClient
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import bcrypt_context
from app.models import RoleEnum, User
from .fixtures.fixture_users import TEST_PASSWORD
from .utils import check_db_data, check_db_fields, check_json_data


class TestAuthAPI:
    """Класс для тестирования API авторизации."""

    url = '/api/v1/auth/login/'

    async def test_anon_user_can_login(
        self,
        customer_client: AsyncClient,
        customer: User
    ):
        """Тест для проверки входа в свой профиль анонимным пользователем."""
        data = {'username': customer.username, 'password': TEST_PASSWORD}
        response = await customer_client.post(self.url, data=data)
        assert response.status_code == HTTPStatus.CREATED, response.json()

    async def test_anon_user_cant_login_with_invalid_data(
        self,
        client: AsyncClient
    ):
        """
        Тест для проверки невозможности войти в свой профиль
        с невалидными данными анонимным пользователем.
        """
        data = {'username': 'invalid_username', 'password': 'invalid_pass'}
        response = await client.post(self.url, data=data)
        assert response.status_code == HTTPStatus.BAD_REQUEST


class TestUserAPI:
    """Класс для тестирования API пользователей."""

    me_url = '/api/v1/users/me/'
    registration_url = '/api/v1/users/registration/'

    async def test_auth_user_can_get_own_profile(
        self,
        customer_client: AsyncClient,
        customer: User,
        user_response_data: dict[str, Any]
    ):
        """Тест для проверки получения профиля авторизованным пользователем."""
        response = await customer_client.get(self.me_url)
        assert response.status_code == HTTPStatus.OK, response.json()
        expected_data = {k: getattr(customer, k) for k in user_response_data}
        check_json_data(response, expected_data)

    async def test_anon_user_cant_get_profile(self, client: AsyncClient):
        """
        Тест для проверки невозможности получения
        профиля без данных анонимным пользователем.
        """
        response = await client.get(self.me_url)
        assert response.status_code == HTTPStatus.UNAUTHORIZED

    @pytest.mark.parametrize(
        'role',
        (RoleEnum.CUSTOMER, RoleEnum.SUPPLIER, RoleEnum.ADMIN),
        ids=('customer', 'supplier', 'admin')
    )
    async def test_anon_user_can_create_profile(
        self,
        client: AsyncClient,
        test_db_session: AsyncSession,
        user_request_data: dict[str, str],
        user_response_data: dict[str, Any],
        role: str
    ):
        """Тест для проверки создания профиля анонимным пользователем."""
        user_request_data['role'] = role
        response = await client.post(
            self.registration_url,
            json=user_request_data
        )
        assert response.status_code == HTTPStatus.CREATED, response.json()
        check_json_data(response, user_response_data)
        users = (await test_db_session.scalars(select(User))).all()
        assert len(users) == 1
        user = users[0]
        bcrypt_context.verify(user_request_data['password'], user.password)
        check_db_data(response, user_response_data, user)

    @pytest.mark.parametrize('field', ('username', 'email'))
    async def test_anon_user_cant_create_profile_with_already_exists_data(
        self,
        client: AsyncClient,
        test_db_session: AsyncSession,
        user_request_data: dict[str, str],
        customer: User,
        field: str
    ):
        """
        Тест для проверки невозможности создания профиля с
        уже существующими данными анонимным пользователем.
        """
        data = {**user_request_data, field: getattr(customer, field)}
        response = await client.post(self.registration_url, json=data)
        assert response.status_code == HTTPStatus.BAD_REQUEST
        count = await test_db_session.scalar(
            select(func.count()).select_from(User)
        )
        assert count == 1

    @pytest.mark.parametrize(
        'invalid_data',
        ({'role': 'no'}, {'email': 'no'}),
        ids=('invalid_role', 'invalid_email')
    )
    async def test_anon_user_cant_create_profile_with_invalid_data(
        self,
        client: AsyncClient,
        test_db_session: AsyncSession,
        user_request_data: dict[str, str],
        invalid_data: dict[str, str]
    ):
        """
        Тест для проверки невозможности создания профиля
        с невалидными данными аноннимным пользователем.
        """
        user_request_data.update(invalid_data)
        response = await client.post(
            self.registration_url,
            json=user_request_data
        )
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
        count = await test_db_session.scalar(
            select(func.count()).select_from(User)
        )
        assert count == 0

    async def test_auth_user_can_patch_own_profile(
        self,
        customer_client: AsyncClient,
        customer: AsyncSession,
        user_request_data: dict[str, str],
        user_response_data: dict[str, Any]
    ):
        """Тест для проверки изменения профиля авторизованным пользователем."""
        response = await customer_client.patch(
            self.me_url,
            json=user_request_data
        )
        assert response.status_code == HTTPStatus.OK, response.json()
        check_json_data(response, user_response_data)
        bcrypt_context.verify(user_request_data['password'], customer.password)
        check_db_data(response, user_response_data, customer)

    @pytest.mark.parametrize('field', ('username', 'email'))
    async def test_auth_user_cant_patch_own_profile_with_already_exists_data(
        self,
        customer_client: AsyncClient,
        customer: User,
        supplier_1: User,
        field: str
    ):
        """
        Тест для проверки невозможности изменения профиля на уже
        существующие данные авторизованным пользователем.
        """
        data = {field: getattr(supplier_1, field)}
        expected_value = getattr(customer, field)
        response = await customer_client.patch(self.me_url, json=data)
        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert getattr(customer, field) == expected_value

    async def test_auth_user_cant_patch_own_role(
        self,
        customer_client: AsyncClient,
        customer: User
    ):
        """
        Тест для проверки невозможности изменения
        роли авторизованным пользователем.
        """
        response = await customer_client.patch(
            self.me_url,
            json={'role': RoleEnum.SUPPLIER}
        )
        assert response.status_code == HTTPStatus.OK
        assert response.json()['role'] == RoleEnum.CUSTOMER
        assert customer.role == RoleEnum.CUSTOMER

    async def test_anon_user_cant_patch_profile(
        self,
        client: AsyncClient,
        user_request_data: dict[str, str]
    ):
        """
        Тест для проверки невозможности изменения
        профиля анонимным пользователем.
        """
        response = await client.patch(self.me_url, json=user_request_data)
        assert response.status_code == HTTPStatus.UNAUTHORIZED

    async def test_auth_user_can_delete_own_profile(
        self,
        customer_client: AsyncClient,
        test_db_session: AsyncSession
    ):
        """Тест для проверки удаления профиля авторизованным пользователем."""
        response = await customer_client.delete(self.me_url)
        assert response.status_code == HTTPStatus.NO_CONTENT
        count = await test_db_session.scalar(
            select(func.count()).select_from(User)
        )
        assert count == 0

    async def test_anon_user_cant_delete_profile(self, client: AsyncClient):
        """
        Тест для проверки невозможности удаления
        профиля анонимным пользователем.
        """
        response = await client.delete(self.me_url)
        assert response.status_code == HTTPStatus.UNAUTHORIZED


class TestUserModel:
    """Класс для тестирования модели User."""

    def test_model_user_fields(self):
        """Тест для проверки наличия полей модели User."""
        expected_fields = (
            'id', 'first_name', 'last_name',
            'username', 'email', 'role', 'password'
        )
        check_db_fields(expected_fields, User)
