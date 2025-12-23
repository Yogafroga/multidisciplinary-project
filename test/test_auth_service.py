"""
Тесты для сервиса авторизации (services/auth.py).

Покрывает:
- Создание JWT токенов
- Проверка токенов
- Аутентификация пользователей
- Хеширование паролей
"""
import pytest
from datetime import timedelta, datetime, UTC
from jose import jwt
from fastapi import HTTPException


class TestAuthService:
    """Тесты для сервиса авторизации."""

    @pytest.mark.unit
    def test_create_access_token(self):
        """Тест создания JWT токена."""
        from backend.app.services.auth import create_access_token, SECRET_KEY, ALGORITHM

        token = create_access_token(
            login="testuser",
            user_id=1,
            expires_delta=timedelta(minutes=30)
        )

        assert token is not None
        assert isinstance(token, str)

        # Проверяем что токен можно декодировать
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert payload["sub"] == "testuser"
        assert payload["id"] == 1
        assert "exp" in payload

    @pytest.mark.unit
    def test_create_access_token_expiration(self):
        """Тест что токен содержит правильное время истечения."""
        from backend.app.services.auth import create_access_token, SECRET_KEY, ALGORITHM

        expires_delta = timedelta(minutes=60)
        before = datetime.now(UTC)

        token = create_access_token(
            login="testuser",
            user_id=1,
            expires_delta=expires_delta
        )

        after = datetime.now(UTC)

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        exp_time = datetime.fromtimestamp(payload["exp"], tz=UTC)

        # Время истечения должно быть в пределах before + delta и after + delta
        assert exp_time >= before + expires_delta - timedelta(seconds=1)
        assert exp_time <= after + expires_delta + timedelta(seconds=1)

    @pytest.mark.unit
    def test_bcrypt_hash_and_verify(self):
        """Тест хеширования и проверки пароля."""
        from backend.app.services.auth import bcrypt_context

        password = "mysecurepassword123"
        hashed = bcrypt_context.hash(password)

        # Хеш не должен быть равен паролю
        assert hashed != password

        # Проверка правильного пароля
        assert bcrypt_context.verify(password, hashed) is True

        # Проверка неправильного пароля
        assert bcrypt_context.verify("wrongpassword", hashed) is False

    @pytest.mark.unit
    def test_bcrypt_different_hashes(self):
        """Тест что одинаковые пароли дают разные хеши (соль)."""
        from backend.app.services.auth import bcrypt_context

        password = "samepassword"
        hash1 = bcrypt_context.hash(password)
        hash2 = bcrypt_context.hash(password)

        # Хеши должны быть разными из-за соли
        assert hash1 != hash2

        # Но оба должны валидироваться
        assert bcrypt_context.verify(password, hash1) is True
        assert bcrypt_context.verify(password, hash2) is True

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_current_user_valid_token(self):
        """Тест получения текущего пользователя по валидному токену."""
        from backend.app.services.auth import get_current_user, create_access_token

        token = create_access_token(
            login="testuser",
            user_id=42,
            expires_delta=timedelta(minutes=30)
        )

        user = await get_current_user(token)

        assert user["username"] == "testuser"
        assert user["user_id"] == 42

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_current_user_invalid_token(self):
        """Тест получения пользователя по невалидному токену."""
        from backend.app.services.auth import get_current_user

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user("invalid.token.here")

        assert exc_info.value.status_code == 401
        assert "Could not validate credentials" in exc_info.value.detail

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_current_user_expired_token(self):
        """Тест получения пользователя по истекшему токену."""
        from backend.app.services.auth import get_current_user, create_access_token

        # Создаем токен с отрицательным временем жизни
        token = create_access_token(
            login="testuser",
            user_id=1,
            expires_delta=timedelta(seconds=-10)
        )

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(token)

        assert exc_info.value.status_code == 401

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_current_user_missing_fields(self):
        """Тест токена без обязательных полей."""
        from backend.app.services.auth import get_current_user, SECRET_KEY, ALGORITHM
        from jose import jwt

        # Создаем токен без поля 'id'
        payload = {
            "sub": "testuser",
            "exp": datetime.now(UTC) + timedelta(minutes=30)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(token)

        assert exc_info.value.status_code == 401

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_authenticate_user_success(self, test_session):
        """Тест успешной аутентификации пользователя."""
        from backend.app.services.auth import authenticate_user, bcrypt_context
        from backend.app.models.user import User
        from backend.app.models.user_role import User_role

        # Создаем роль и пользователя
        role = User_role(id=1, role="user")
        test_session.add(role)
        await test_session.commit()

        user = User(
            login="authuser",
            password_hash=bcrypt_context.hash("correctpassword"),
            role_id=1
        )
        test_session.add(user)
        await test_session.commit()

        result = await authenticate_user("authuser", "correctpassword", test_session)

        assert result is not False
        assert result.login == "authuser"

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_authenticate_user_wrong_password(self, test_session):
        """Тест аутентификации с неверным паролем."""
        from backend.app.services.auth import authenticate_user, bcrypt_context
        from backend.app.models.user import User
        from backend.app.models.user_role import User_role

        role = User_role(id=1, role="user")
        test_session.add(role)
        await test_session.commit()

        user = User(
            login="authuser2",
            password_hash=bcrypt_context.hash("correctpassword"),
            role_id=1
        )
        test_session.add(user)
        await test_session.commit()

        result = await authenticate_user("authuser2", "wrongpassword", test_session)

        assert result is False

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_authenticate_user_not_found(self, test_session):
        """Тест аутентификации несуществующего пользователя."""
        from backend.app.services.auth import authenticate_user

        result = await authenticate_user("nonexistent", "anypassword", test_session)

        assert result is False

    @pytest.mark.unit
    def test_oauth2_bearer_scheme(self):
        """Тест настройки OAuth2 схемы."""
        from backend.app.services.auth import oauth2_bearer

        assert oauth2_bearer.scheme_name == "OAuth2PasswordBearer"
        assert "api/auth/token" in oauth2_bearer.model.flows.password.tokenUrl
