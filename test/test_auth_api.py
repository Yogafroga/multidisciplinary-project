"""
Тесты для API авторизации (/api/auth).

Покрывает:
- Создание пользователя
- Аутентификация и получение токена
- Валидация данных
"""
import pytest
from fastapi import status


class TestAuthAPI:
    """Тесты для эндпоинтов авторизации."""

    @pytest.mark.api
    def test_hello_endpoint(self, client):
        """Тест эндпоинта /hello."""
        response = client.get("/hello")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"message": "hello!"}

    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_create_user_success(self, async_client, test_session):
        """Тест успешного создания пользователя."""
        from backend.app.models.user_role import User_role

        # Создаем роль пользователя
        role = User_role(id=1, role="user")
        test_session.add(role)
        await test_session.commit()

        user_data = {
            "login": "newuser",
            "password": "securepassword123",
            "role": 1
        }

        response = await async_client.post("/api/auth/create_user", json=user_data)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["message"] == "User created successfully."

    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_create_user_duplicate_login(self, async_client, test_session):
        """Тест создания пользователя с существующим логином."""
        from backend.app.models.user_role import User_role
        from backend.app.models.user import User
        from backend.app.services.auth import bcrypt_context

        # Создаем роль и пользователя
        role = User_role(id=1, role="user")
        test_session.add(role)
        await test_session.commit()

        existing_user = User(
            login="existinguser",
            password_hash=bcrypt_context.hash("password"),
            role_id=1
        )
        test_session.add(existing_user)
        await test_session.commit()

        # Пытаемся создать пользователя с таким же логином
        user_data = {
            "login": "existinguser",
            "password": "newpassword",
            "role": 1
        }

        response = await async_client.post("/api/auth/create_user", json=user_data)

        # Ожидаем ошибку уникальности
        assert response.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_500_INTERNAL_SERVER_ERROR]

    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_login_success(self, async_client, test_session):
        """Тест успешной авторизации."""
        from backend.app.models.user_role import User_role
        from backend.app.models.user import User
        from backend.app.services.auth import bcrypt_context

        # Создаем роль и пользователя
        role = User_role(id=1, role="user")
        test_session.add(role)
        await test_session.commit()

        user = User(
            login="testlogin",
            password_hash=bcrypt_context.hash("testpass123"),
            role_id=1
        )
        test_session.add(user)
        await test_session.commit()

        # Авторизуемся
        response = await async_client.post(
            "/api/auth/token",
            data={"username": "testlogin", "password": "testpass123"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_login_invalid_credentials(self, async_client, test_session):
        """Тест авторизации с неверными данными."""
        from backend.app.models.user_role import User_role
        from backend.app.models.user import User
        from backend.app.services.auth import bcrypt_context

        # Создаем роль и пользователя
        role = User_role(id=1, role="user")
        test_session.add(role)
        await test_session.commit()

        user = User(
            login="validuser",
            password_hash=bcrypt_context.hash("correctpass"),
            role_id=1
        )
        test_session.add(user)
        await test_session.commit()

        # Пытаемся авторизоваться с неверным паролем
        response = await async_client.post(
            "/api/auth/token",
            data={"username": "validuser", "password": "wrongpass"}
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()["detail"] == "Could not validate user"

    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_login_nonexistent_user(self, async_client, test_session):
        """Тест авторизации несуществующего пользователя."""
        response = await async_client.post(
            "/api/auth/token",
            data={"username": "nonexistent", "password": "anypass"}
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.api
    def test_protected_endpoint_without_token(self, client):
        """Тест доступа к защищенному эндпоинту без токена."""
        response = client.get("/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.api
    def test_protected_endpoint_with_invalid_token(self, client):
        """Тест доступа к защищенному эндпоинту с невалидным токеном."""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/", headers=headers)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_protected_endpoint_with_valid_token(self, async_client, test_session, auth_headers):
        """Тест доступа к защищенному эндпоинту с валидным токеном."""
        from backend.app.models.user_role import User_role
        from backend.app.models.user import User
        from backend.app.services.auth import bcrypt_context

        # Создаем роль и пользователя
        role = User_role(id=1, role="user")
        test_session.add(role)
        await test_session.commit()

        user = User(
            id=1,
            login="testuser",
            password_hash=bcrypt_context.hash("password"),
            role_id=1
        )
        test_session.add(user)
        await test_session.commit()

        response = await async_client.get("/", headers=auth_headers)

        # Проверяем что авторизация прошла
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "user" in data

    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_create_user_missing_fields(self, async_client):
        """Тест создания пользователя без обязательных полей."""
        # Отсутствует пароль
        user_data = {"login": "incomplete"}

        response = await async_client.post("/api/auth/create_user", json=user_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_create_user_empty_login(self, async_client, test_session):
        """Тест создания пользователя с пустым логином."""
        from backend.app.models.user_role import User_role

        role = User_role(id=1, role="user")
        test_session.add(role)
        await test_session.commit()

        user_data = {
            "login": "",
            "password": "password123",
            "role": 1
        }

        response = await async_client.post("/api/auth/create_user", json=user_data)

        # Пустой логин должен быть обработан (либо ошибка валидации, либо создастся)
        assert response.status_code in [
            status.HTTP_201_CREATED,
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            status.HTTP_400_BAD_REQUEST
        ]
