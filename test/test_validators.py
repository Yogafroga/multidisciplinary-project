"""
Тесты для валидаторов (utils/validators.py).

Покрывает:
- Валидация MIME типов
- Проверка сигнатур файлов
- Проверка размера файлов
- Проверка целостности изображений
"""
import pytest
from io import BytesIO
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi import HTTPException, UploadFile


class TestImageValidator:
    """Тесты для ImageValidator."""

    @pytest.mark.unit
    def test_known_signatures(self):
        """Тест наличия известных сигнатур."""
        from backend.app.utils.validators import ImageValidator

        assert "image/jpeg" in ImageValidator.KNOWN_SIGNATURES
        assert "image/png" in ImageValidator.KNOWN_SIGNATURES
        assert "image/gif" in ImageValidator.KNOWN_SIGNATURES
        assert "image/webp" in ImageValidator.KNOWN_SIGNATURES

    @pytest.mark.unit
    def test_jpeg_signature(self):
        """Тест сигнатуры JPEG."""
        from backend.app.utils.validators import ImageValidator

        signature = ImageValidator.KNOWN_SIGNATURES["image/jpeg"]
        # JPEG начинается с FFD8FF
        assert signature == b"\xFF\xD8\xFF"

    @pytest.mark.unit
    def test_png_signature(self):
        """Тест сигнатуры PNG."""
        from backend.app.utils.validators import ImageValidator

        signature = ImageValidator.KNOWN_SIGNATURES["image/png"]
        # PNG signature
        assert signature == b"\x89\x50\x4E\x47\x0D\x0A\x1A\x0A"

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_validate_valid_jpeg(self, sample_image_bytes):
        """Тест валидации корректного JPEG."""
        with patch('backend.app.utils.validators.settings') as mock_settings:
            mock_settings.max_bytes = 10 * 1024 * 1024  # 10MB
            mock_settings.ALLOWED_MIME_TYPES = {"image/jpeg", "image/png"}
            mock_settings.MAX_FILE_SIZE_MB = 10

            from backend.app.utils.validators import ImageValidator

            validator = ImageValidator()

            file = UploadFile(
                file=BytesIO(sample_image_bytes),
                filename="test.jpg",
                size=len(sample_image_bytes),
                headers={"content-type": "image/jpeg"}
            )

            # Мокаем PIL.Image для упрощения
            with patch('backend.app.utils.validators.Image') as mock_pil:
                mock_img = MagicMock()
                mock_pil.open.return_value = mock_img

                result = await validator.validate(file)

                assert result is not None

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_validate_unsupported_mime_type(self):
        """Тест отклонения неподдерживаемого MIME типа."""
        with patch('backend.app.utils.validators.settings') as mock_settings:
            mock_settings.max_bytes = 10 * 1024 * 1024
            mock_settings.ALLOWED_MIME_TYPES = {"image/jpeg", "image/png"}
            mock_settings.MAX_FILE_SIZE_MB = 10

            from backend.app.utils.validators import ImageValidator

            validator = ImageValidator()

            file = UploadFile(
                file=BytesIO(b"fake pdf content"),
                filename="doc.pdf",
                size=100,
                headers={"content-type": "application/pdf"}
            )

            with pytest.raises(HTTPException) as exc_info:
                await validator.validate(file)

            assert exc_info.value.status_code == 400
            assert "не поддерживается" in exc_info.value.detail

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_validate_fake_jpeg(self):
        """Тест отклонения поддельного JPEG (неправильная сигнатура)."""
        with patch('backend.app.utils.validators.settings') as mock_settings:
            mock_settings.max_bytes = 10 * 1024 * 1024
            mock_settings.ALLOWED_MIME_TYPES = {"image/jpeg", "image/png"}
            mock_settings.MAX_FILE_SIZE_MB = 10

            from backend.app.utils.validators import ImageValidator

            validator = ImageValidator()

            # Файл с MIME jpeg, но без правильной сигнатуры
            fake_content = b"This is not a real JPEG file"
            file = UploadFile(
                file=BytesIO(fake_content),
                filename="fake.jpg",
                size=len(fake_content),
                headers={"content-type": "image/jpeg"}
            )

            with pytest.raises(HTTPException) as exc_info:
                await validator.validate(file)

            assert exc_info.value.status_code == 400
            assert "поддельный" in exc_info.value.detail.lower()

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_validate_too_large_file(self, sample_image_bytes):
        """Тест отклонения слишком большого файла."""
        with patch('backend.app.utils.validators.settings') as mock_settings:
            mock_settings.max_bytes = 100  # Очень маленький лимит
            mock_settings.ALLOWED_MIME_TYPES = {"image/jpeg", "image/png"}
            mock_settings.MAX_FILE_SIZE_MB = 0.0001

            from backend.app.utils.validators import ImageValidator

            validator = ImageValidator()

            # Файл больше лимита
            large_content = sample_image_bytes + b'\x00' * 1000
            file = UploadFile(
                file=BytesIO(large_content),
                filename="large.jpg",
                size=len(large_content),
                headers={"content-type": "image/jpeg"}
            )

            with pytest.raises(HTTPException) as exc_info:
                await validator.validate(file)

            assert exc_info.value.status_code == 413
            assert "большой" in exc_info.value.detail.lower()

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_validate_corrupted_image(self, sample_image_bytes):
        """Тест отклонения поврежденного изображения."""
        with patch('backend.app.utils.validators.settings') as mock_settings:
            mock_settings.max_bytes = 10 * 1024 * 1024
            mock_settings.ALLOWED_MIME_TYPES = {"image/jpeg", "image/png"}
            mock_settings.MAX_FILE_SIZE_MB = 10

            from backend.app.utils.validators import ImageValidator

            validator = ImageValidator()

            # Начинается как JPEG, но поврежден
            corrupted = b'\xFF\xD8\xFF' + b'corrupted data here'
            file = UploadFile(
                file=BytesIO(corrupted),
                filename="corrupted.jpg",
                size=len(corrupted),
                headers={"content-type": "image/jpeg"}
            )

            with patch('backend.app.utils.validators.Image') as mock_pil:
                mock_pil.open.side_effect = Exception("Cannot identify image file")

                with pytest.raises(HTTPException) as exc_info:
                    await validator.validate(file)

                assert exc_info.value.status_code == 400
                assert "поврежден" in exc_info.value.detail.lower()

    @pytest.mark.unit
    def test_config_integrity_check(self):
        """Тест проверки целостности конфига при инициализации."""
        with patch('backend.app.utils.validators.settings') as mock_settings:
            # Конфиг с неизвестным MIME типом
            mock_settings.max_bytes = 10 * 1024 * 1024
            mock_settings.ALLOWED_MIME_TYPES = {"image/jpeg", "image/unknown_format"}
            mock_settings.MAX_FILE_SIZE_MB = 10

            from backend.app.utils.validators import ImageValidator

            with pytest.raises(RuntimeError) as exc_info:
                ImageValidator()

            assert "image/unknown_format" in str(exc_info.value)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_validate_png(self, sample_png_bytes):
        """Тест валидации PNG файла."""
        with patch('backend.app.utils.validators.settings') as mock_settings:
            mock_settings.max_bytes = 10 * 1024 * 1024
            mock_settings.ALLOWED_MIME_TYPES = {"image/jpeg", "image/png"}
            mock_settings.MAX_FILE_SIZE_MB = 10

            from backend.app.utils.validators import ImageValidator

            validator = ImageValidator()

            file = UploadFile(
                file=BytesIO(sample_png_bytes),
                filename="test.png",
                size=len(sample_png_bytes),
                headers={"content-type": "image/png"}
            )

            with patch('backend.app.utils.validators.Image') as mock_pil:
                mock_img = MagicMock()
                mock_pil.open.return_value = mock_img

                result = await validator.validate(file)

                assert result is not None

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_file_cursor_reset(self, sample_image_bytes):
        """Тест что курсор файла сбрасывается после валидации."""
        with patch('backend.app.utils.validators.settings') as mock_settings:
            mock_settings.max_bytes = 10 * 1024 * 1024
            mock_settings.ALLOWED_MIME_TYPES = {"image/jpeg"}
            mock_settings.MAX_FILE_SIZE_MB = 10

            from backend.app.utils.validators import ImageValidator

            validator = ImageValidator()

            file_io = BytesIO(sample_image_bytes)
            file = UploadFile(
                file=file_io,
                filename="test.jpg",
                size=len(sample_image_bytes),
                headers={"content-type": "image/jpeg"}
            )

            with patch('backend.app.utils.validators.Image') as mock_pil:
                mock_img = MagicMock()
                mock_pil.open.return_value = mock_img

                await validator.validate(file)

                # Курсор должен быть в начале после валидации
                assert file_io.tell() == 0


class TestFileHelper:
    """Тесты для helpers/file_helper.py."""

    @pytest.mark.unit
    def test_generate_filename(self):
        """Тест генерации уникального имени файла."""
        from backend.app.helpers.file_helper import generate_filename

        original = "my_photo.jpg"
        generated = generate_filename(original)

        # Должен быть UUID + расширение
        assert generated.endswith(".jpg")
        assert generated != original
        # UUID имеет 36 символов + .jpg = 40
        assert len(generated) == 40

    @pytest.mark.unit
    def test_generate_filename_preserves_extension(self):
        """Тест сохранения расширения."""
        from backend.app.helpers.file_helper import generate_filename

        assert generate_filename("photo.PNG").endswith(".png")
        assert generate_filename("image.JPEG").endswith(".jpeg")
        assert generate_filename("pic.GIF").endswith(".gif")

    @pytest.mark.unit
    def test_generate_filename_no_extension(self):
        """Тест файла без расширения."""
        from backend.app.helpers.file_helper import generate_filename

        generated = generate_filename("noextension")

        # Должен добавить .bin
        assert generated.endswith(".bin")

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_save_file_to_folder(self, create_upload_file, tmp_path):
        """Тест сохранения файла в папку."""
        from backend.app.helpers.file_helper import save_file_to_folder

        with patch('backend.app.helpers.file_helper.settings') as mock_settings:
            mock_settings.UPLOAD_DIR = tmp_path

            file = create_upload_file(filename="test_save.jpg")

            result = await save_file_to_folder(file, "test_batch")

            assert "file_path" in result
            assert "filename" in result
            assert "original_filename" in result
            assert result["original_filename"] == "test_save.jpg"
            assert result["subfolder"] == "test_batch"
            assert result["file_size"] > 0

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_save_file_to_folder_creates_directories(self, create_upload_file, tmp_path):
        """Тест создания директорий при сохранении."""
        from backend.app.helpers.file_helper import save_file_to_folder

        with patch('backend.app.helpers.file_helper.settings') as mock_settings:
            mock_settings.UPLOAD_DIR = tmp_path / "new_folder"

            file = create_upload_file()

            result = await save_file_to_folder(file, "new_batch")

            # Директория должна быть создана
            assert (tmp_path / "new_folder" / "new_batch").exists()

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_save_file_to_s3(self, create_upload_file):
        """Тест сохранения файла в S3."""
        from backend.app.helpers.file_helper import save_file_to_s3

        with patch('backend.app.helpers.file_helper.settings') as mock_settings, \
             patch('backend.app.helpers.file_helper.aioboto3') as mock_boto:

            mock_settings.VK_S3_ENDPOINT_URL = "https://s3.example.com"
            mock_settings.VK_S3_BUCKET_NAME = "test-bucket"
            mock_settings.VK_S3_ACCESS_KEY_ID = "key"
            mock_settings.VK_S3_SECRET_KEY = "secret"
            mock_settings.VK_S3_REGION = "us-east-1"

            mock_client = AsyncMock()
            mock_client.put_object = AsyncMock()

            mock_session = MagicMock()
            mock_session.client.return_value.__aenter__.return_value = mock_client
            mock_boto.Session.return_value = mock_session

            file = create_upload_file()

            result = await save_file_to_s3(file, "s3_batch")

            assert "url" in result
            assert "s3.example.com" in result["url"]
            assert result["subfolder"] == "s3_batch"

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_save_file_to_s3_with_client(self, create_upload_file):
        """Тест сохранения в S3 с переданным клиентом."""
        from backend.app.helpers.file_helper import save_file_to_s3

        with patch('backend.app.helpers.file_helper.settings') as mock_settings:
            mock_settings.VK_S3_ENDPOINT_URL = "https://s3.example.com"
            mock_settings.VK_S3_BUCKET_NAME = "test-bucket"
            mock_settings.VK_S3_REGION = "us-east-1"

            mock_client = AsyncMock()
            mock_client.put_object = AsyncMock()

            file = create_upload_file()

            result = await save_file_to_s3(file, "batch", s3_client=mock_client)

            mock_client.put_object.assert_called_once()
            assert result is not None
