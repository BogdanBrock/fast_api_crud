"""Модуль создания тестов для пользователей."""

from http import HTTPStatus

import pytest
from pytest_lazy_fixtures import lf
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from httpx import AsyncClient

from app.models import User, RoleEnum
from .utils import check_json_data, check_db_data, check_db_fields
from app.core.user import bcrypt_context
from .fixtures.fixture_users import TEST_PASSWORD


class TestAuthAPI:
    """Класс для тестирования API авторизации."""

    url = '/api/v1/auth/login/'

    async def test_anon_user_can_login(
        self,
        customer_client: AsyncClient,
        customer: User
    ):
        """Тест для проверки правильных данных пользователя при входе."""
        data = {'username': customer.username, 'password': TEST_PASSWORD}
        response = await customer_client.post(self.url, data=data)
        assert response.status_code == HTTPStatus.CREATED, response.json()

    async def test_anon_user_cant_login_with_invalid_data(
        self,
        client: AsyncClient
    ):
        """Тест для проверки неправильных данных пользователя при входе."""
        data = {'username': 'invalid_username', 'password': 'invalid_pass'}
        response = await client.post(self.url, data=data)
        assert response.status_code == HTTPStatus.BAD_REQUEST


class TestUserAPI:
    """Класс для тестирования API пользователей."""

    me_url = '/api/v1/users/me/'
    registration_url = '/api/v1/users/registration/'

    request_data = {
        'first_name': 'test_user',
        'last_name': 'test_user',
        'username': 'test_user',
        'email': 'test_user@example.com',
        'password': 'test_password12345'
    }
    expected_data = {
        'id': 1,
        'first_name': request_data['first_name'],
        'last_name': request_data['last_name'],
        'username': request_data['username'],
        'email': request_data['email'],
    }

    async def test_user_can_get_own_profile(
        self,
        customer_client: AsyncClient,
        customer: User
    ):
        """Тест для получения профиля авторизированным пользователем."""
        response = await customer_client.get(self.me_url)
        assert response.status_code == HTTPStatus.OK, response.json()
        expected_data = {k: getattr(customer, k) for k in self.expected_data}
        check_json_data(response, expected_data)

    async def test_anon_user_cant_get_profile(self, client: AsyncClient):
        """Тест для получения профиля анонимным пользователем."""
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
        role: str
    ):
        """Тест для создания профиля анонимным пользователем."""
        self.request_data['role'] = role
        response = await client.post(
            self.registration_url,
            json=self.request_data
        )
        assert response.status_code == HTTPStatus.CREATED, response.json()
        check_json_data(response, self.expected_data)
        users = (await test_db_session.scalars(select(User))).all()
        assert len(users) == 1
        user = users[0]
        bcrypt_context.verify(self.request_data['password'], user.password)
        check_db_data(response, self.expected_data, user)

    @pytest.mark.parametrize('field', ('username', 'email'))
    async def test_anon_user_cant_create_profile_with_already_exists_data(
        self,
        client: AsyncClient,
        test_db_session: AsyncSession,
        customer: User,
        field: str
    ):
        """Тест для создания профиля с уже существующими данными анонимным пользователем."""
        data = {**self.request_data, field: getattr(customer, field)}
        response = await client.post(self.registration_url, json=data)
        assert response.status_code == HTTPStatus.BAD_REQUEST
        count = await test_db_session.scalar(
            select(func.count()).select_from(User)
        )
        assert count == 1

    @pytest.mark.parametrize(
        'data',
        ({}, {**request_data, 'role': 'no'}, {**request_data, 'email': 'no'}),
        ids=('empty_data', 'invalid_role', 'invalid_email')
    )
    async def test_anon_user_cant_create_profile_with_invalid_data(
        self,
        client: AsyncClient,
        test_db_session: AsyncSession,
        data: dict
    ):
        """Тест создания профиля с невалидными данными анон. пользователем."""
        response = await client.post(self.registration_url, json=data)
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
        count = await test_db_session.scalar(
            select(func.count()).select_from(User)
        )
        assert count == 0

    async def test_auth_user_can_patch_own_profile(
        self,
        customer_client: AsyncClient,
        customer: AsyncSession
    ):
        """Тест для обновления профиля авторизированным пользователем."""
        response = await customer_client.patch(
            self.me_url,
            json=self.request_data
        )
        assert response.status_code == HTTPStatus.OK, response.json()
        check_json_data(response, self.expected_data)
        bcrypt_context.verify(self.request_data['password'], customer.password)
        check_db_data(response, self.expected_data, customer)

    @pytest.mark.parametrize('field', ('username', 'email'))
    async def test_auth_user_cant_patch_own_profile_with_already_exists_data(
        self,
        customer_client: AsyncClient,
        customer: User,
        supplier_1: User,
        field: str
    ):
        """Тест для обновления профиля на уже существующие данные авторизированным пользователем."""
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
        """Тест для обновления роли авторизированным пользователем."""
        response = await customer_client.patch(
            self.me_url,
            json={'role': RoleEnum.SUPPLIER}
        )
        assert response.status_code == HTTPStatus.OK
        assert response.json()['role'] == RoleEnum.CUSTOMER
        assert customer.role == RoleEnum.CUSTOMER

    async def test_anon_user_cant_patch_profile(self, client: AsyncClient):
        response = await client.patch(self.me_url, json=self.request_data)
        assert response.status_code == HTTPStatus.UNAUTHORIZED

    async def test_user_can_delete_own_profile(
        self,
        customer_client: AsyncClient,
        test_db_session: AsyncSession
    ):
        """Тест для удаления профиля авторизированным пользователем."""
        response = await customer_client.delete(self.me_url)
        assert response.status_code == HTTPStatus.NO_CONTENT
        count = await test_db_session.scalar(
            select(func.count()).select_from(User)
        )
        assert count == 0

    async def test_anon_user_cant_delete_profile(self, client: AsyncClient):
        """Тест для удаления профиля анонимным пользователем."""
        response = await client.delete(self.me_url)
        assert response.status_code == HTTPStatus.UNAUTHORIZED


class TestUserModel:
    """Класс для тестирования модели User."""

    def test_model_fields(self):
        """Тест для проверки наличия полей модели User."""
        expected_fields = (
            'id', 'first_name', 'last_name',
            'username', 'email', 'role', 'password'
        )
        check_db_fields(expected_fields, User)
