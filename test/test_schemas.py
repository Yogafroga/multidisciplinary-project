"""
Тесты для Pydantic схем (schemas/).

Покрывает:
- Схемы загрузки (upload.py)
- Схемы истории (history.py)
- Схемы пользователей (user.py)
- Схемы токенов (token.py)
"""
import pytest
from datetime import datetime
from pydantic import ValidationError


class TestUploadSchemas:
    """Тесты для схем загрузки."""

    @pytest.mark.unit
    def test_file_upload_result_success(self):
        """Тест успешного результата загрузки."""
        from backend.schemas.upload import FileUploadResult

        result = FileUploadResult(
            filename="cow.jpg",
            status="success",
            image_id=1,
            image_url="/media/batch/cow.jpg",
            animal_id="COW001",
            weight=450.5
        )

        assert result.filename == "cow.jpg"
        assert result.status == "success"
        assert result.image_id == 1
        assert result.weight == 450.5

    @pytest.mark.unit
    def test_file_upload_result_failed(self):
        """Тест неудачного результата загрузки."""
        from backend.schemas.upload import FileUploadResult

        result = FileUploadResult(
            filename="bad.pdf",
            status="failed",
            error="Unsupported file type"
        )

        assert result.status == "failed"
        assert result.error == "Unsupported file type"
        assert result.image_id is None

    @pytest.mark.unit
    def test_file_upload_result_minimal(self):
        """Тест минимального результата загрузки."""
        from backend.schemas.upload import FileUploadResult

        result = FileUploadResult(
            filename="test.jpg",
            status="pending"
        )

        assert result.filename == "test.jpg"
        assert result.status == "pending"
        assert result.image_id is None
        assert result.weight is None

    @pytest.mark.unit
    def test_upload_images_response(self):
        """Тест ответа на загрузку изображений."""
        from backend.schemas.upload import UploadImagesResponse, FileUploadResult

        files = [
            FileUploadResult(filename="cow1.jpg", status="success", weight=400),
            FileUploadResult(filename="cow2.jpg", status="success", weight=450),
        ]

        response = UploadImagesResponse(
            batch_id="abc-123-def",
            files=files
        )

        assert response.batch_id == "abc-123-def"
        assert len(response.files) == 2

    @pytest.mark.unit
    def test_archive_file_detail(self):
        """Тест деталей файла из архива."""
        from backend.schemas.upload import ArchiveFileDetail

        detail = ArchiveFileDetail(
            filename="cow_001.jpg",
            status="success",
            image_id=1,
            image_url="/media/archive/cow_001.jpg",
            weight=420.0,
            confidence=0.95
        )

        assert detail.filename == "cow_001.jpg"
        assert detail.weight == 420.0
        assert detail.confidence == 0.95

    @pytest.mark.unit
    def test_archive_summary(self):
        """Тест сводки по архиву."""
        from backend.schemas.upload import ArchiveSummary

        summary = ArchiveSummary(
            total_weight=1350.0,
            average_weight=450.0,
            animal_count=3,
            min_weight=400.0,
            max_weight=500.0
        )

        assert summary.total_weight == 1350.0
        assert summary.average_weight == 450.0
        assert summary.animal_count == 3

    @pytest.mark.unit
    def test_archive_summary_minimal(self):
        """Тест минимальной сводки."""
        from backend.schemas.upload import ArchiveSummary

        summary = ArchiveSummary(
            total_weight=0.0,
            average_weight=0.0,
            animal_count=0
        )

        assert summary.min_weight is None
        assert summary.max_weight is None

    @pytest.mark.unit
    def test_upload_archive_response(self):
        """Тест ответа на загрузку архива."""
        from backend.schemas.upload import UploadArchiveResponse, ArchiveSummary, ArchiveFileDetail

        summary = ArchiveSummary(
            total_weight=900.0,
            average_weight=450.0,
            animal_count=2,
            min_weight=400.0,
            max_weight=500.0
        )

        details = [
            ArchiveFileDetail(filename="cow1.jpg", status="success", weight=400),
            ArchiveFileDetail(filename="cow2.jpg", status="success", weight=500),
        ]

        response = UploadArchiveResponse(
            archive_id="archive-uuid",
            total_images=2,
            processed_images=2,
            failed_images=0,
            summary=summary,
            details=details
        )

        assert response.archive_id == "archive-uuid"
        assert response.total_images == 2
        assert response.summary.total_weight == 900.0


class TestHistorySchemas:
    """Тесты для схем истории."""

    @pytest.mark.unit
    def test_history_item(self):
        """Тест элемента истории."""
        from backend.schemas.history import HistoryItem

        item = HistoryItem(
            id=1,
            animal_id="COW001",
            weight=450.5,
            weight_units="kg",
            confidence=0.95,
            image_url="/media/batch/cow.jpg",
            created_at=datetime.now(),
            created_by="testuser",
            batch_id="batch-uuid"
        )

        assert item.id == 1
        assert item.animal_id == "COW001"
        assert item.weight_units == "kg"

    @pytest.mark.unit
    def test_history_item_optional_fields(self):
        """Тест опциональных полей элемента истории."""
        from backend.schemas.history import HistoryItem

        item = HistoryItem(
            id=2,
            weight_units="kg",
            image_url="/media/test.jpg",
            created_at=datetime.now(),
            created_by="admin",
            batch_id="batch-2"
        )

        assert item.animal_id is None
        assert item.weight is None
        assert item.confidence is None

    @pytest.mark.unit
    def test_history_response(self):
        """Тест ответа со списком истории."""
        from backend.schemas.history import HistoryResponse, HistoryItem

        items = [
            HistoryItem(
                id=i,
                weight_units="kg",
                image_url=f"/media/img{i}.jpg",
                created_at=datetime.now(),
                created_by="user",
                batch_id="batch"
            )
            for i in range(5)
        ]

        response = HistoryResponse(
            page=1,
            limit=20,
            total=100,
            total_pages=5,
            data=items
        )

        assert response.page == 1
        assert response.total == 100
        assert len(response.data) == 5

    @pytest.mark.unit
    def test_delete_history_response(self):
        """Тест ответа на удаление истории."""
        from backend.schemas.history import DeleteHistoryResponse

        response = DeleteHistoryResponse(message="Record deleted successfully")

        assert response.message == "Record deleted successfully"


class TestUserSchemas:
    """Тесты для схем пользователей."""

    @pytest.mark.unit
    def test_user_schema(self):
        """Тест схемы пользователя."""
        from backend.schemas.user import User

        user = User(
            login="testuser",
            password_hash="hashed_password"
        )

        assert user.login == "testuser"
        assert user.password_hash == "hashed_password"

    @pytest.mark.unit
    def test_create_user_schema(self):
        """Тест схемы создания пользователя."""
        from backend.schemas.user import CreateUser

        create_user = CreateUser(
            login="newuser",
            password="securepassword123",
            role=1
        )

        assert create_user.login == "newuser"
        assert create_user.password == "securepassword123"
        assert create_user.role == 1

    @pytest.mark.unit
    def test_create_user_validation(self):
        """Тест валидации при создании пользователя."""
        from backend.schemas.user import CreateUser

        # Все поля обязательны
        with pytest.raises(ValidationError):
            CreateUser(login="nopassword")


class TestTokenSchemas:
    """Тесты для схем токенов."""

    @pytest.mark.unit
    def test_token_schema(self):
        """Тест схемы токена."""
        from backend.schemas.token import Token

        token = Token(
            access_token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            token_type="bearer"
        )

        assert token.access_token.startswith("eyJ")
        assert token.token_type == "bearer"

    @pytest.mark.unit
    def test_token_type_case_insensitive(self):
        """Тест что token_type может быть в разных регистрах."""
        from backend.schemas.token import Token

        token = Token(
            access_token="token123",
            token_type="Bearer"
        )

        assert token.token_type == "Bearer"
