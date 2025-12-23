"""
Тесты для сервиса архивов (services/archive_service.py).

Покрывает:
- Обработка ZIP архивов
- Извлечение ID животных из имен файлов
- Расчет сводной статистики
- Обработка ошибок
"""
import pytest
import zipfile
from io import BytesIO
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
import uuid


class TestArchiveService:
    """Тесты для сервиса архивов."""

    @pytest.mark.unit
    def test_extract_animal_id_with_underscore(self):
        """Тест извлечения ID животного из имени с underscore."""
        from backend.app.services.archive_service import ArchiveService

        service = ArchiveService()

        # cow_001.jpg -> 001
        assert service._extract_animal_id("cow_001.jpg") == "001"

        # bull_A123.jpg -> A123
        assert service._extract_animal_id("bull_A123.jpg") == "A123"

        # farm_cow_456.jpg -> 456
        assert service._extract_animal_id("farm_cow_456.jpg") == "456"

    @pytest.mark.unit
    def test_extract_animal_id_without_underscore(self):
        """Тест извлечения ID из имени без underscore."""
        from backend.app.services.archive_service import ArchiveService

        service = ArchiveService()

        # image123.jpg -> image123
        assert service._extract_animal_id("image123.jpg") == "image123"

        # photo.jpg -> photo
        assert service._extract_animal_id("photo.jpg") == "photo"

    @pytest.mark.unit
    def test_extract_animal_id_nested_path(self):
        """Тест извлечения ID из пути с папками."""
        from backend.app.services.archive_service import ArchiveService

        service = ArchiveService()

        # folder/cow_007.jpg -> 007
        assert service._extract_animal_id("folder/cow_007.jpg") == "007"

    @pytest.mark.unit
    def test_create_upload_file(self, sample_image_bytes):
        """Тест создания UploadFile из байтов."""
        from backend.app.services.archive_service import ArchiveService

        service = ArchiveService()

        upload_file = service._create_upload_file(
            filename="test_image.jpg",
            content=sample_image_bytes,
            ext=".jpg"
        )

        assert upload_file.filename == "test_image.jpg"
        assert upload_file.content_type == "image/jpeg"
        assert upload_file.size == len(sample_image_bytes)

    @pytest.mark.unit
    def test_create_upload_file_png(self, sample_png_bytes):
        """Тест создания UploadFile для PNG."""
        from backend.app.services.archive_service import ArchiveService

        service = ArchiveService()

        upload_file = service._create_upload_file(
            filename="image.png",
            content=sample_png_bytes,
            ext=".png"
        )

        assert upload_file.content_type == "image/png"

    @pytest.mark.unit
    def test_calculate_summary_with_data(self):
        """Тест расчета сводной статистики."""
        from backend.app.services.archive_service import ArchiveService

        service = ArchiveService()

        successful = [
            {"filename": "cow1.jpg", "weight": 400.0},
            {"filename": "cow2.jpg", "weight": 450.0},
            {"filename": "cow3.jpg", "weight": 500.0},
        ]

        summary = service.calculate_summary(successful)

        assert summary["total_weight"] == 1350.0
        assert summary["average_weight"] == 450.0
        assert summary["animal_count"] == 3
        assert summary["min_weight"] == 400.0
        assert summary["max_weight"] == 500.0

    @pytest.mark.unit
    def test_calculate_summary_empty(self):
        """Тест сводки для пустого списка."""
        from backend.app.services.archive_service import ArchiveService

        service = ArchiveService()

        summary = service.calculate_summary([])

        assert summary["total_weight"] == 0.0
        assert summary["average_weight"] == 0.0
        assert summary["animal_count"] == 0
        assert summary["min_weight"] is None
        assert summary["max_weight"] is None

    @pytest.mark.unit
    def test_calculate_summary_with_none_weights(self):
        """Тест сводки когда некоторые веса None."""
        from backend.app.services.archive_service import ArchiveService

        service = ArchiveService()

        successful = [
            {"filename": "cow1.jpg", "weight": 400.0},
            {"filename": "cow2.jpg", "weight": None},
            {"filename": "cow3.jpg", "weight": 500.0},
        ]

        summary = service.calculate_summary(successful)

        # None веса должны быть проигнорированы
        assert summary["total_weight"] == 900.0
        assert summary["average_weight"] == 450.0
        assert summary["animal_count"] == 2

    @pytest.mark.unit
    def test_calculate_summary_single_item(self):
        """Тест сводки для одного элемента."""
        from backend.app.services.archive_service import ArchiveService

        service = ArchiveService()

        successful = [{"filename": "cow.jpg", "weight": 420.5}]

        summary = service.calculate_summary(successful)

        assert summary["total_weight"] == 420.5
        assert summary["average_weight"] == 420.5
        assert summary["min_weight"] == 420.5
        assert summary["max_weight"] == 420.5

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_process_archive_success(self, test_session, sample_zip_bytes):
        """Тест успешной обработки архива."""
        from backend.app.services.archive_service import ArchiveService
        from backend.app.models.user_role import UserRole
        from backend.app.models.user import User
        from backend.app.services.auth import bcrypt_context
        from fastapi import UploadFile

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

        service = ArchiveService()

        with patch('backend.app.services.archive_service.image_service') as mock_image_service, \
             patch('backend.app.services.archive_service.settings') as mock_settings:

            mock_settings.VK_S3_ENDPOINT_URL = None
            mock_settings.VK_S3_ACCESS_KEY_ID = None

            mock_image_service.process_file_upload = AsyncMock(return_value={
                "original_filename": "test.jpg",
                "url_path": "/media/batch/test.jpg"
            })

            mock_image = MagicMock()
            mock_image.id = 1
            mock_image.url_path = "/media/batch/test.jpg"

            mock_detection = MagicMock()
            mock_detection.weight = 450.0
            mock_detection.confidence = 0.95

            mock_image_service.create_db_entries = AsyncMock(return_value=(mock_image, mock_detection))

            # Создаем UploadFile из zip bytes
            upload_file = UploadFile(
                file=BytesIO(sample_zip_bytes),
                filename="archive.zip",
                size=len(sample_zip_bytes)
            )

            successful, failed = await service.process_archive(
                file=upload_file,
                batch_id=str(uuid.uuid4()),
                user_id=1,
                session=test_session
            )

            assert len(successful) > 0
            assert len(failed) == 0

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_process_archive_bad_zip(self, test_session):
        """Тест обработки поврежденного ZIP."""
        from backend.app.services.archive_service import ArchiveService
        from backend.app.models.user_role import UserRole
        from backend.app.models.user import User
        from backend.app.services.auth import bcrypt_context
        from fastapi import UploadFile

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

        service = ArchiveService()

        # Некорректный ZIP
        bad_zip = b"This is not a valid zip file"
        upload_file = UploadFile(
            file=BytesIO(bad_zip),
            filename="bad.zip",
            size=len(bad_zip)
        )

        successful, failed = await service.process_archive(
            file=upload_file,
            batch_id=str(uuid.uuid4()),
            user_id=1,
            session=test_session
        )

        assert len(successful) == 0
        assert len(failed) == 1
        assert "Некорректный ZIP-архив" in failed[0]["error"]

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_process_archive_skips_macosx_files(self, test_session, sample_image_bytes):
        """Тест что __MACOSX файлы пропускаются."""
        from backend.app.services.archive_service import ArchiveService
        from backend.app.models.user_role import UserRole
        from backend.app.models.user import User
        from backend.app.services.auth import bcrypt_context
        from fastapi import UploadFile

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

        # Создаем ZIP с __MACOSX файлами
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zf:
            zf.writestr("cow_001.jpg", sample_image_bytes)
            zf.writestr("__MACOSX/._cow_001.jpg", b"metadata")
            zf.writestr(".hidden.jpg", sample_image_bytes)
        zip_buffer.seek(0)

        service = ArchiveService()

        with patch('backend.app.services.archive_service.image_service') as mock_service, \
             patch('backend.app.services.archive_service.settings') as mock_settings:

            mock_settings.VK_S3_ENDPOINT_URL = None
            mock_settings.VK_S3_ACCESS_KEY_ID = None

            mock_service.process_file_upload = AsyncMock(return_value={
                "original_filename": "cow_001.jpg",
                "url_path": "/media/batch/cow_001.jpg"
            })

            mock_image = MagicMock()
            mock_image.id = 1
            mock_image.url_path = "/media/batch/cow_001.jpg"
            mock_detection = MagicMock()
            mock_detection.weight = 450.0
            mock_detection.confidence = 0.95

            mock_service.create_db_entries = AsyncMock(return_value=(mock_image, mock_detection))

            upload_file = UploadFile(
                file=zip_buffer,
                filename="archive.zip"
            )

            successful, failed = await service.process_archive(
                file=upload_file,
                batch_id=str(uuid.uuid4()),
                user_id=1,
                session=test_session
            )

            # Только cow_001.jpg должен быть обработан
            assert len(successful) == 1
            assert successful[0]["filename"] == "cow_001.jpg"

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_process_archive_skips_non_images(self, test_session, sample_image_bytes):
        """Тест что не-изображения пропускаются."""
        from backend.app.services.archive_service import ArchiveService
        from backend.app.models.user_role import UserRole
        from backend.app.models.user import User
        from backend.app.services.auth import bcrypt_context
        from fastapi import UploadFile

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

        # ZIP с разными типами файлов
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zf:
            zf.writestr("cow_001.jpg", sample_image_bytes)
            zf.writestr("readme.txt", b"This is a text file")
            zf.writestr("data.csv", b"col1,col2\n1,2")
        zip_buffer.seek(0)

        service = ArchiveService()

        with patch('backend.app.services.archive_service.image_service') as mock_service, \
             patch('backend.app.services.archive_service.settings') as mock_settings:

            mock_settings.VK_S3_ENDPOINT_URL = None
            mock_settings.VK_S3_ACCESS_KEY_ID = None

            mock_service.process_file_upload = AsyncMock(return_value={
                "original_filename": "cow_001.jpg",
                "url_path": "/media/batch/cow_001.jpg"
            })

            mock_image = MagicMock()
            mock_image.id = 1
            mock_image.url_path = "/media/batch/cow_001.jpg"
            mock_detection = MagicMock()
            mock_detection.weight = 450.0
            mock_detection.confidence = 0.95

            mock_service.create_db_entries = AsyncMock(return_value=(mock_image, mock_detection))

            upload_file = UploadFile(
                file=zip_buffer,
                filename="archive.zip"
            )

            successful, failed = await service.process_archive(
                file=upload_file,
                batch_id=str(uuid.uuid4()),
                user_id=1,
                session=test_session
            )

            # Только jpg должен быть обработан
            assert len(successful) == 1

    @pytest.mark.unit
    def test_mime_type_mapping(self):
        """Тест корректного маппинга MIME типов."""
        from backend.app.services.archive_service import ArchiveService

        service = ArchiveService()

        jpg_file = service._create_upload_file("test.jpg", b"data", ".jpg")
        assert jpg_file.content_type == "image/jpeg"

        jpeg_file = service._create_upload_file("test.jpeg", b"data", ".jpeg")
        assert jpeg_file.content_type == "image/jpeg"

        png_file = service._create_upload_file("test.png", b"data", ".png")
        assert png_file.content_type == "image/png"

        gif_file = service._create_upload_file("test.gif", b"data", ".gif")
        assert gif_file.content_type == "image/gif"

        webp_file = service._create_upload_file("test.webp", b"data", ".webp")
        assert webp_file.content_type == "image/webp"
