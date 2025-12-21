"""
Конфигурация pytest для тестирования CattleWeighAI Backend.
Содержит общие фикстуры для всех тестов.
"""
import os
import sys
import asyncio
from datetime import timedelta
from io import BytesIO
from pathlib import Path
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock, patch
import uuid

import pytest
import pytest_asyncio
from fastapi import UploadFile
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

# Добавляем путь к корню проекта
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Устанавливаем тестовые переменные окружения ДО импорта приложения
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-testing-only")
os.environ.setdefault("DB_NAME", "test_db")
os.environ.setdefault("DB_HOST", "localhost")
os.environ.setdefault("DB_PORT", "5432")
os.environ.setdefault("DB_USERNAME", "test_user")
os.environ.setdefault("DB_PASSWORD", "test_password")
os.environ.setdefault("VK_S3_BUCKET_NAME", "test-bucket")
os.environ.setdefault("VK_S3_ACCESS_KEY_ID", "test-access-key")
os.environ.setdefault("VK_S3_SECRET_KEY", "test-secret-key")


# Теперь импортируем приложение и модели
from backend.app.database import Base
from backend.app.main import app
from backend.app.services.auth import create_access_token, bcrypt_context


# Тестовая база данных SQLite в памяти
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop():
    """Создание event loop для всей тестовой сессии."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def test_engine():
    """Создание тестового движка БД."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def test_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Создание тестовой сессии БД."""
    async_session_maker = async_sessionmaker(
        test_engine,
        expire_on_commit=False,
        class_=AsyncSession
    )

    async with async_session_maker() as session:
        yield session
        await session.rollback()


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """Синхронный тестовый клиент FastAPI."""
    with TestClient(app) as c:
        yield c


@pytest_asyncio.fixture
async def async_client(test_session) -> AsyncGenerator[AsyncClient, None]:
    """Асинхронный тестовый клиент FastAPI."""
    from backend.app.database import get_db

    async def override_get_db():
        yield test_session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
def test_user_data() -> dict:
    """Тестовые данные пользователя."""
    return {
        "login": "testuser",
        "password": "testpassword123",
        "role": 1
    }


@pytest.fixture
def test_user_token() -> str:
    """Генерация тестового JWT токена."""
    return create_access_token(
        login="testuser",
        user_id=1,
        expires_delta=timedelta(minutes=30)
    )


@pytest.fixture
def auth_headers(test_user_token) -> dict:
    """Заголовки авторизации для тестовых запросов."""
    return {"Authorization": f"Bearer {test_user_token}"}


@pytest.fixture
def mock_current_user() -> dict:
    """Мок данных текущего пользователя."""
    return {"username": "testuser", "user_id": 1}


@pytest.fixture
def sample_image_bytes() -> bytes:
    """Создание тестовых байтов изображения JPEG."""
    # Минимальный валидный JPEG
    return (
        b'\xFF\xD8\xFF\xE0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00'
        b'\xFF\xDB\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t'
        b'\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a'
        b'\x1f\x1e\x1d\x1a\x1c\x1c $.\' ",#\x1c\x1c(7),01444\x1f\'9telephones:\x00'
        b'\xFF\xC0\x00\x0b\x08\x00\x01\x00\x01\x01\x01\x11\x00'
        b'\xFF\xC4\x00\x1f\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00'
        b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b'
        b'\xFF\xC4\x00\xb5\x10\x00\x02\x01\x03\x03\x02\x04\x03\x05\x05\x04\x04\x00\x00\x01}'
        b'\x01\x02\x03\x00\x04\x11\x05\x12!1A\x06\x13Qa\x07"q\x142\x81\x91\xa1\x08#B'
        b'\xb1\xc1\x15R\xd1\xf0$3br\x82\t\n\x16\x17\x18\x19\x1a%&\'()*456789'
        b':CDEFGHIJSTUVWXYZcdefghijstuvwxyz\x83\x84\x85\x86\x87\x88\x89\x8a'
        b'\x92\x93\x94\x95\x96\x97\x98\x99\x9a\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa'
        b'\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca'
        b'\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xe1\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea'
        b'\xf1\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa'
        b'\xFF\xDA\x00\x08\x01\x01\x00\x00?\x00\xfb\xd5\x00\x00\x00\x00'
        b'\xFF\xD9'
    )


@pytest.fixture
def sample_png_bytes() -> bytes:
    """Создание тестовых байтов изображения PNG."""
    # Минимальный валидный PNG (1x1 пиксель)
    return (
        b'\x89PNG\r\n\x1a\n'  # PNG signature
        b'\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde'
        b'\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x18\xd8N'
        b'\x00\x00\x00\x00IEND\xaeB`\x82'
    )


@pytest.fixture
def create_upload_file(sample_image_bytes):
    """Фабрика для создания тестовых UploadFile объектов."""
    def _create_upload_file(
        filename: str = "test_image.jpg",
        content: bytes = None,
        content_type: str = "image/jpeg"
    ) -> UploadFile:
        if content is None:
            content = sample_image_bytes

        file_obj = BytesIO(content)
        return UploadFile(
            file=file_obj,
            filename=filename,
            size=len(content),
            headers={"content-type": content_type}
        )

    return _create_upload_file


@pytest.fixture
def sample_zip_bytes(sample_image_bytes) -> bytes:
    """Создание тестового ZIP архива с изображениями."""
    import zipfile

    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.writestr("cow_001.jpg", sample_image_bytes)
        zip_file.writestr("cow_002.jpg", sample_image_bytes)
        zip_file.writestr("cow_003.jpg", sample_image_bytes)

    zip_buffer.seek(0)
    return zip_buffer.read()


@pytest.fixture
def mock_s3_client():
    """Мок S3 клиента."""
    mock_client = AsyncMock()
    mock_client.put_object = AsyncMock(return_value=None)
    return mock_client


@pytest.fixture
def mock_ml_adapter():
    """Мок ML адаптера для предсказания веса."""
    mock_adapter = MagicMock()
    mock_adapter.predict_async = AsyncMock(return_value={
        "predicted_weight": 450.5,
        "confidence": "high",
        "cattle_percentage": 0.95
    })
    return mock_adapter


@pytest.fixture
def mock_settings():
    """Мок настроек приложения."""
    with patch('backend.app.core.config.settings') as mock:
        mock.UPLOAD_DIR = Path("/tmp/test_uploads")
        mock.MAX_FILE_SIZE_MB = 5
        mock.max_bytes = 5 * 1024 * 1024
        mock.ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}
        mock.VK_S3_ENDPOINT_URL = None
        mock.VK_S3_BUCKET_NAME = None
        mock.VK_S3_ACCESS_KEY_ID = None
        mock.VK_S3_SECRET_KEY = None
        mock.ML_ENABLED = False
        yield mock


# Маркеры для категоризации тестов
def pytest_configure(config):
    """Регистрация кастомных маркеров."""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "api: API endpoint tests")
    config.addinivalue_line("markers", "slow: Slow running tests")
