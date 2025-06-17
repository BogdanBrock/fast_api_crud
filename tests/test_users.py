"""Модуль создания тестов для пользователей."""

from http import HTTPStatus

import pytest
from sqlalchemy import select, func
from httpx import AsyncClient
from pytest_lazy_fixtures import lf

from app.models import User, RoleEnum


class TestUserAPI:
    """Класс для тестирования API пользователей."""

    me_url = '/api/v1/users/me/'
    data = {
        "first_name": "test_user",
        "last_name": "test_user",
        "username": "test_user",
        "email": "test_user@example.com",
        "password": "test_password12345",
    }

    @pytest.mark.parametrize(
        'user_client',
        (lf('customer_client'), lf('supplier_1_client'), lf('admin_client'))
    )
    async def test_user_can_get_own_profile(self, user_client: AsyncClient):
        response = await user_client.get(self.me_url)
        assert response.status_code == HTTPStatus.OK, response.json()

    async def test_anon_user_cant_get_profile(self, client: AsyncClient):
        response = await client.get(self.me_url)
        assert response.status_code == HTTPStatus.UNAUTHORIZED

    @pytest.mark.parametrize(
        'role',
        (RoleEnum.CUSTOMER, RoleEnum.SUPPLIER, RoleEnum.ADMIN)
    )
    async def test_user_can_create_profile(
        self,
        client: AsyncClient,
        role: str
    ):
        self.data['role'] = role
        response = await client.post(
            '/api/v1/users/registration/',
            json=self.data
        )
        assert response.status_code == HTTPStatus.CREATED

    @pytest.mark.parametrize(
        'user_client',
        (lf('customer_client'), lf('supplier_1_client'), lf('admin_client'))
    )
    async def test_user_can_update_own_profile(self, user_client: AsyncClient):
        response = await user_client.patch(self.me_url, json=self.data)
        assert response.status_code == HTTPStatus.OK

    async def test_anon_user_cant_update_profile(self, client: AsyncClient):
        response = await client.patch(self.me_url, json=self.data)
        assert response.status_code == HTTPStatus.UNAUTHORIZED

    @pytest.mark.skip
    @pytest.mark.parametrize(
        'user_client, old_role, new_role',
        (
            (lf('customer_client'), RoleEnum.CUSTOMER, RoleEnum.SUPPLIER),
            (lf('supplier_1_client'), RoleEnum.SUPPLIER, RoleEnum.CUSTOMER),
            (lf('admin_client'), RoleEnum.ADMIN, RoleEnum.CUSTOMER)
        )
    )
    async def test_user_cant_update_own_role(
        self,
        user_client: AsyncClient,
        old_role: str,
        new_role: str
    ):
        response = await user_client.patch(
            self.me_url,
            json={'role': new_role}
        )
        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert response.json()['role'] == old_role

    @pytest.mark.parametrize(
        'user_client',
        (lf('customer_client'), lf('supplier_1_client'), lf('admin_client'))
    )
    async def test_user_can_delete_own_profile(
        self,
        test_db_session: AsyncClient,
        user_client: AsyncClient
    ):
        response = await user_client.delete(self.me_url)
        assert response.status_code == HTTPStatus.NO_CONTENT
        count = await test_db_session.scalar(
            select(func.count()).select_from(User)
        )
        assert count == 0

    async def test_user_cant_delete_profile(self, client: AsyncClient):
        response = await client.delete(self.me_url)
        assert response.status_code == HTTPStatus.UNAUTHORIZED

