"""
Тесты для сервиса изображений (services/image_service.py).

Покрывает:
- Загрузка изображений
- Сохранение в файловую систему
- Сохранение в S3
- Создание записей в БД
- Предсказание веса
"""
import pytest
from io import BytesIO
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
import uuid


class TestImageService:
    """Тесты для сервиса изображений."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_process_file_upload_local(self, create_upload_file, mock_settings):
        """Тест загрузки файла в локальную папку."""
        from backend.app.services.image_service import ImageService

        service = ImageService()

        with patch('backend.app.services.image_service.save_file_to_folder') as mock_save:
            mock_save.return_value = {
                "file_path": "/tmp/uploads/batch/file.jpg",
                "filename": "file.jpg",
                "original_filename": "test.jpg",
                "subfolder": "batch",
                "file_size": 1024,
                "mime_type": "image/jpeg",
                "url": "/media/batch/file.jpg"
            }

            file = create_upload_file()
            result = await service.process_file_upload(file, "test-subfolder")

            assert "url_path" in result
            assert result["url_path"] == "/media/test-subfolder/file.jpg"

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_process_file_upload_s3(self, create_upload_file):
        """Тест загрузки файла в S3."""
        from backend.app.services.image_service import ImageService

        service = ImageService()

        with patch('backend.app.services.image_service.settings') as mock_settings, \
             patch('backend.app.services.image_service.save_file_to_s3') as mock_save:

            mock_settings.VK_S3_ENDPOINT_URL = "https://s3.example.com"
            mock_settings.VK_S3_BUCKET_NAME = "test-bucket"
            mock_settings.VK_S3_ACCESS_KEY_ID = "key"
            mock_settings.VK_S3_SECRET_KEY = "secret"

            mock_save.return_value = {
                "file_path": "batch/file.jpg",
                "filename": "file.jpg",
                "original_filename": "test.jpg",
                "subfolder": "batch",
                "file_size": 1024,
                "mime_type": "image/jpeg",
                "url": "https://s3.example.com/test-bucket/batch/file.jpg"
            }

            file = create_upload_file()
            result = await service.process_file_upload(file, "test-subfolder")

            assert "url_path" in result
            assert "s3" in result["url_path"]

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_create_db_entries(self, test_session):
        """Тест создания записей в БД."""
        from backend.app.services.image_service import ImageService
        from backend.app.models.user_role import UserRole
        from backend.app.models.user import User
        from backend.app.models.image_batch import ImageBatch
        from backend.app.services.auth import bcrypt_context

        # Создаем пользователя и батч
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

        batch = ImageBatch(id=1, uid=uuid.uuid4(), user_id=1)
        test_session.add(batch)
        await test_session.commit()

        service = ImageService()

        file_data = {
            "original_filename": "test_cow.jpg",
            "url_path": "/media/batch/test.jpg"
        }

        with patch.object(service, '_predict_weight', new_callable=AsyncMock) as mock_predict:
            mock_predict.return_value = {"predicted_weight": 450.0, "confidence": 0.95}

            image, detection = await service.create_db_entries(
                session=test_session,
                file_data=file_data,
                batch_id=1,
                animal_id="COW001",
                image_bytes=b"fake_image_data"
            )

            assert image.id is not None
            assert image.url_path == "/media/batch/test.jpg"
            assert detection.id is not None
            assert detection.animal_id == "COW001"
            assert detection.weight == 450.0

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_predict_weight_with_ml(self):
        """Тест предсказания веса с ML моделью."""
        from backend.app.services.image_service import ImageService

        service = ImageService()

        with patch('backend.app.services.image_service._get_cattle_adapter') as mock_get_adapter:
            mock_adapter = MagicMock()
            mock_adapter.predict_async = AsyncMock(return_value={
                "predicted_weight": 500.0,
                "confidence": "high",
                "cattle_percentage": 0.92
            })
            mock_get_adapter.return_value = mock_adapter

            result = await service._predict_weight(b"image_bytes")

            assert result["predicted_weight"] == 500.0
            assert result["confidence"] == 0.95  # high -> 0.95

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_predict_weight_ml_disabled(self):
        """Тест предсказания когда ML отключен."""
        from backend.app.services.image_service import ImageService

        service = ImageService()

        with patch('backend.app.services.image_service._get_cattle_adapter', return_value=None):
            result = await service._predict_weight(b"image_bytes")

            # Fallback значения
            assert result["predicted_weight"] == 0
            assert result["confidence"] == 0

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_predict_weight_no_image_bytes(self):
        """Тест предсказания без байтов изображения."""
        from backend.app.services.image_service import ImageService

        service = ImageService()

        result = await service._predict_weight(None)

        assert result["predicted_weight"] == 0
        assert result["confidence"] == 0

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_predict_weight_ml_error(self):
        """Тест обработки ошибки ML модели."""
        from backend.app.services.image_service import ImageService

        service = ImageService()

        with patch('backend.app.services.image_service._get_cattle_adapter') as mock_get_adapter:
            mock_adapter = MagicMock()
            mock_adapter.predict_async = AsyncMock(side_effect=Exception("ML Error"))
            mock_get_adapter.return_value = mock_adapter

            result = await service._predict_weight(b"image_bytes")

            # Fallback при ошибке
            assert result["predicted_weight"] == 0
            assert result["confidence"] == 0

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_upload_image_full_flow(self, test_session, create_upload_file):
        """Тест полного процесса загрузки изображения."""
        from backend.app.services.image_service import ImageService
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

        service = ImageService()

        with patch.object(service, 'process_file_upload', new_callable=AsyncMock) as mock_process, \
             patch.object(service, '_predict_weight', new_callable=AsyncMock) as mock_predict:

            mock_process.return_value = {
                "original_filename": "test.jpg",
                "url_path": "/media/batch/test.jpg"
            }
            mock_predict.return_value = {"predicted_weight": 420.0, "confidence": 0.88}

            file = create_upload_file()
            batch_uuid = str(uuid.uuid4())

            image, detection = await service.upload_image(
                file=file,
                subfolder_name=batch_uuid,
                user_id=1,
                session=test_session,
                animal_id="BULL007"
            )

            assert image is not None
            assert detection is not None
            assert detection.animal_id == "BULL007"
            assert detection.weight == 420.0

    @pytest.mark.unit
    def test_lazy_ml_adapter_loading(self):
        """Тест ленивой загрузки ML адаптера."""
        from backend.app.services.image_service import _get_cattle_adapter

        with patch('backend.app.services.image_service.settings') as mock_settings:
            mock_settings.ML_ENABLED = False

            adapter = _get_cattle_adapter()
            assert adapter is None

    @pytest.mark.unit
    def test_low_confidence_conversion(self):
        """Тест конвертации низкой уверенности."""
        from backend.app.services.image_service import ImageService
        import asyncio

        service = ImageService()

        with patch('backend.app.services.image_service._get_cattle_adapter') as mock_get_adapter:
            mock_adapter = MagicMock()
            mock_adapter.predict_async = AsyncMock(return_value={
                "predicted_weight": 300.0,
                "confidence": "low",  # не high
                "cattle_percentage": 0.5
            })
            mock_get_adapter.return_value = mock_adapter

            result = asyncio.get_event_loop().run_until_complete(
                service._predict_weight(b"image_bytes")
            )

            assert result["confidence"] == 0.65  # low -> 0.65
