"""
Тесты для API загрузки изображений (/upload_images).

Покрывает:
- Загрузка одиночных изображений
- Валидация файлов
- Определение веса
"""
import pytest
from io import BytesIO
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi import status
import uuid


class TestUploadImageAPI:
    """Тесты для эндпоинта загрузки изображений."""

    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_upload_image_unauthorized(self, async_client, sample_image_bytes):
        """Тест загрузки без авторизации."""
        files = {"file": ("test.jpg", BytesIO(sample_image_bytes), "image/jpeg")}
        data = {"animal_id": "001"}

        response = await async_client.post(
            "/upload_images",
            files=files,
            data=data
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_upload_image_success(self, async_client, test_session, auth_headers, sample_image_bytes):
        """Тест успешной загрузки изображения."""
        from backend.app.models.user_role import UserRole
        from backend.app.models.user import User
        from backend.app.services.auth import bcrypt_context

        # Создаем пользователя
        role = UserRole(id=1, name="user")
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

        # Мокаем сервисы
        with patch('backend.app.api.uploadImage.image_service') as mock_service, \
             patch('backend.app.api.uploadImage.image_validator') as mock_validator:

            # Настраиваем моки
            mock_file = MagicMock()
            mock_file.filename = "test.jpg"
            mock_validator.validate = AsyncMock(return_value=mock_file)

            mock_image = MagicMock()
            mock_image.id = 1
            mock_image.url_path = "/media/test/image.jpg"

            mock_detection = MagicMock()
            mock_detection.weight = 450.5

            mock_service.upload_image = AsyncMock(return_value=(mock_image, mock_detection))

            files = {"file": ("test.jpg", BytesIO(sample_image_bytes), "image/jpeg")}
            data = {"animal_id": "COW001"}

            response = await async_client.post(
                "/upload_images",
                files=files,
                data=data,
                headers=auth_headers
            )

            assert response.status_code == status.HTTP_201_CREATED
            result = response.json()
            assert "batch_id" in result
            assert len(result["files"]) == 1
            assert result["files"][0]["status"] == "success"
            assert result["files"][0]["weight"] == 450.5

    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_upload_image_missing_animal_id(self, async_client, test_session, auth_headers, sample_image_bytes):
        """Тест загрузки без указания animal_id."""
        from backend.app.models.user_role import UserRole
        from backend.app.models.user import User
        from backend.app.services.auth import bcrypt_context

        role = UserRole(id=1, name="user")
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

        files = {"file": ("test.jpg", BytesIO(sample_image_bytes), "image/jpeg")}

        response = await async_client.post(
            "/upload_images",
            files=files,
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_upload_image_invalid_format(self, async_client, test_session, auth_headers):
        """Тест загрузки файла неподдерживаемого формата."""
        from backend.app.models.user_role import UserRole
        from backend.app.models.user import User
        from backend.app.services.auth import bcrypt_context
        from fastapi import HTTPException

        role = UserRole(id=1, name="user")
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

        with patch('backend.app.api.uploadImage.image_validator') as mock_validator:
            mock_validator.validate = AsyncMock(
                side_effect=HTTPException(
                    status_code=400,
                    detail="Тип файла 'application/pdf' не поддерживается"
                )
            )

            files = {"file": ("test.pdf", BytesIO(b"%PDF-1.4 test"), "application/pdf")}
            data = {"animal_id": "001"}

            response = await async_client.post(
                "/upload_images",
                files=files,
                data=data,
                headers=auth_headers
            )

            assert response.status_code == status.HTTP_201_CREATED
            result = response.json()
            assert result["files"][0]["status"] == "failed"

    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_upload_image_too_large(self, async_client, test_session, auth_headers):
        """Тест загрузки слишком большого файла."""
        from backend.app.models.user_role import UserRole
        from backend.app.models.user import User
        from backend.app.services.auth import bcrypt_context
        from fastapi import HTTPException

        role = UserRole(id=1, name="user")
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

        with patch('backend.app.api.uploadImage.image_validator') as mock_validator:
            mock_validator.validate = AsyncMock(
                side_effect=HTTPException(
                    status_code=413,
                    detail="Файл слишком большой. Лимит: 5 МБ"
                )
            )

            # Создаем большой файл
            large_content = b'\xFF\xD8\xFF' + b'\x00' * (6 * 1024 * 1024)
            files = {"file": ("large.jpg", BytesIO(large_content), "image/jpeg")}
            data = {"animal_id": "001"}

            response = await async_client.post(
                "/upload_images",
                files=files,
                data=data,
                headers=auth_headers
            )

            assert response.status_code == status.HTTP_201_CREATED
            result = response.json()
            assert result["files"][0]["status"] == "failed"

    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_upload_image_service_error(self, async_client, test_session, auth_headers, sample_image_bytes):
        """Тест обработки ошибки сервиса."""
        from backend.app.models.user_role import UserRole
        from backend.app.models.user import User
        from backend.app.services.auth import bcrypt_context

        role = UserRole(id=1, name="user")
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

        with patch('backend.app.api.uploadImage.image_service') as mock_service, \
             patch('backend.app.api.uploadImage.image_validator') as mock_validator:

            mock_file = MagicMock()
            mock_file.filename = "test.jpg"
            mock_validator.validate = AsyncMock(return_value=mock_file)
            mock_service.upload_image = AsyncMock(side_effect=Exception("DB Error"))

            files = {"file": ("test.jpg", BytesIO(sample_image_bytes), "image/jpeg")}
            data = {"animal_id": "001"}

            response = await async_client.post(
                "/upload_images",
                files=files,
                data=data,
                headers=auth_headers
            )

            assert response.status_code == status.HTTP_201_CREATED
            result = response.json()
            assert result["files"][0]["status"] == "error"
            assert "Internal processing error" in result["files"][0]["error"]


class TestUploadArchiveAPI:
    """Тесты для эндпоинта загрузки архивов."""

    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_upload_archive_unauthorized(self, async_client, sample_zip_bytes):
        """Тест загрузки архива без авторизации."""
        files = {"file": ("archive.zip", BytesIO(sample_zip_bytes), "application/zip")}

        response = await async_client.post("/upload_archive", files=files)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_upload_archive_success(self, async_client, test_session, auth_headers, sample_zip_bytes):
        """Тест успешной загрузки архива."""
        from backend.app.models.user_role import UserRole
        from backend.app.models.user import User
        from backend.app.services.auth import bcrypt_context

        role = UserRole(id=1, name="user")
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

        with patch('backend.app.api.uploadArchive.archive_service') as mock_service:
            mock_service.process_archive = AsyncMock(return_value=(
                [
                    {"filename": "cow_001.jpg", "status": "success", "image_id": 1, "image_url": "/media/test/1.jpg", "weight": 450.0, "confidence": 0.95},
                    {"filename": "cow_002.jpg", "status": "success", "image_id": 2, "image_url": "/media/test/2.jpg", "weight": 480.0, "confidence": 0.92},
                ],
                []
            ))
            mock_service.calculate_summary = MagicMock(return_value={
                "total_weight": 930.0,
                "average_weight": 465.0,
                "animal_count": 2,
                "min_weight": 450.0,
                "max_weight": 480.0
            })

            files = {"file": ("archive.zip", BytesIO(sample_zip_bytes), "application/zip")}

            response = await async_client.post(
                "/upload_archive",
                files=files,
                headers=auth_headers
            )

            assert response.status_code == status.HTTP_201_CREATED
            result = response.json()
            assert "archive_id" in result
            assert result["total_images"] == 2
            assert result["processed_images"] == 2
            assert result["failed_images"] == 0
            assert result["summary"]["total_weight"] == 930.0
            assert result["summary"]["average_weight"] == 465.0

    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_upload_archive_not_zip(self, async_client, test_session, auth_headers):
        """Тест загрузки файла, который не является ZIP."""
        from backend.app.models.user_role import UserRole
        from backend.app.models.user import User
        from backend.app.services.auth import bcrypt_context

        role = UserRole(id=1, name="user")
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

        files = {"file": ("notzip.txt", BytesIO(b"This is not a zip file"), "text/plain")}

        response = await async_client.post(
            "/upload_archive",
            files=files,
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "ZIP" in response.json()["detail"]

    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_upload_archive_with_failures(self, async_client, test_session, auth_headers, sample_zip_bytes):
        """Тест загрузки архива с частичными ошибками."""
        from backend.app.models.user_role import UserRole
        from backend.app.models.user import User
        from backend.app.services.auth import bcrypt_context

        role = UserRole(id=1, name="user")
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

        with patch('backend.app.api.uploadArchive.archive_service') as mock_service:
            mock_service.process_archive = AsyncMock(return_value=(
                [
                    {"filename": "cow_001.jpg", "status": "success", "image_id": 1, "image_url": "/media/test/1.jpg", "weight": 450.0, "confidence": 0.95},
                ],
                [
                    {"filename": "corrupted.jpg", "status": "error", "error": "Файл поврежден"},
                ]
            ))
            mock_service.calculate_summary = MagicMock(return_value={
                "total_weight": 450.0,
                "average_weight": 450.0,
                "animal_count": 1,
                "min_weight": 450.0,
                "max_weight": 450.0
            })

            files = {"file": ("archive.zip", BytesIO(sample_zip_bytes), "application/zip")}

            response = await async_client.post(
                "/upload_archive",
                files=files,
                headers=auth_headers
            )

            assert response.status_code == status.HTTP_201_CREATED
            result = response.json()
            assert result["total_images"] == 2
            assert result["processed_images"] == 1
            assert result["failed_images"] == 1

    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_upload_archive_service_error(self, async_client, test_session, auth_headers, sample_zip_bytes):
        """Тест обработки ошибки сервиса архивов."""
        from backend.app.models.user_role import UserRole
        from backend.app.models.user import User
        from backend.app.services.auth import bcrypt_context

        role = UserRole(id=1, name="user")
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

        with patch('backend.app.api.uploadArchive.archive_service') as mock_service:
            mock_service.process_archive = AsyncMock(side_effect=Exception("S3 Error"))

            files = {"file": ("archive.zip", BytesIO(sample_zip_bytes), "application/zip")}

            response = await async_client.post(
                "/upload_archive",
                files=files,
                headers=auth_headers
            )

            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
