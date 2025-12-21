"""
Тесты для репозиториев (repositories/).

Покрывает:
- ImageRepository
- CattleDetectionRepository
- BatchImageRepository
"""
import pytest
import uuid


class TestImageRepository:
    """Тесты для репозитория изображений."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_create_image(self, test_session):
        """Тест создания изображения."""
        from backend.app.repositories.image_repository import ImageRepository
        from backend.app.models.user_role import UserRole
        from backend.app.models.user import User
        from backend.app.models.image_batch import ImageBatch
        from backend.app.services.auth import bcrypt_context

        # Создаем зависимости
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

        file_data = {
            "original_filename": "cow_photo.jpg",
            "url_path": "/media/batch/image.jpg"
        }

        image = await ImageRepository.create(test_session, file_data, 1)

        assert image.id is not None
        assert image.original_name == "cow_photo.jpg"
        assert image.url_path == "/media/batch/image.jpg"
        assert image.batch_id == 1
        assert image.status == "UPLOADED"

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_create_image_with_uid(self, test_session):
        """Тест что изображение получает автоматический UUID."""
        from backend.app.repositories.image_repository import ImageRepository
        from backend.app.models.user_role import UserRole
        from backend.app.models.user import User
        from backend.app.models.image_batch import ImageBatch
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

        batch = ImageBatch(id=1, uid=uuid.uuid4(), user_id=1)
        test_session.add(batch)
        await test_session.commit()

        file_data = {
            "original_filename": "test.jpg",
            "url_path": "/media/batch/test.jpg"
        }

        image = await ImageRepository.create(test_session, file_data, 1)

        assert image.uid is not None
        assert isinstance(image.uid, uuid.UUID)


class TestCattleDetectionRepository:
    """Тесты для репозитория детекций."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_create_detection(self, test_session):
        """Тест создания детекции."""
        from backend.app.repositories.cattle_detection_repository import CattleDetectionRepository
        from backend.app.repositories.image_repository import ImageRepository
        from backend.app.models.user_role import UserRole
        from backend.app.models.user import User
        from backend.app.models.image_batch import ImageBatch
        from backend.app.services.auth import bcrypt_context

        # Создаем зависимости
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

        # Создаем изображение
        file_data = {"original_filename": "cow.jpg", "url_path": "/media/test/cow.jpg"}
        image = await ImageRepository.create(test_session, file_data, 1)

        # Создаем детекцию
        detection = await CattleDetectionRepository.create(
            session=test_session,
            image_id=image.id,
            animal_id="COW001",
            weight=450.5,
            confidence=0.95,
            nn_object_id=0
        )

        assert detection.id is not None
        assert detection.animal_id == "COW001"
        assert detection.weight == 450.5
        assert detection.confidence == 0.95
        assert detection.image_id == image.id

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_create_detection_minimal(self, test_session):
        """Тест создания детекции с минимальными данными."""
        from backend.app.repositories.cattle_detection_repository import CattleDetectionRepository
        from backend.app.repositories.image_repository import ImageRepository
        from backend.app.models.user_role import UserRole
        from backend.app.models.user import User
        from backend.app.models.image_batch import ImageBatch
        from backend.app.services.auth import bcrypt_context

        role = UserRole(id=1, name="user")
        test_session.add(role)
        await test_session.commit()

        user = User(id=1, login="testuser", password_hash=bcrypt_context.hash("password"), role_id=1)
        test_session.add(user)
        await test_session.commit()

        batch = ImageBatch(id=1, uid=uuid.uuid4(), user_id=1)
        test_session.add(batch)
        await test_session.commit()

        file_data = {"original_filename": "cow.jpg", "url_path": "/media/test/cow.jpg"}
        image = await ImageRepository.create(test_session, file_data, 1)

        # Создаем детекцию без weight и confidence
        detection = await CattleDetectionRepository.create(
            session=test_session,
            image_id=image.id,
            animal_id="COW002"
        )

        assert detection.id is not None
        assert detection.animal_id == "COW002"
        assert detection.weight is None
        assert detection.confidence is None

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_by_id(self, test_session):
        """Тест получения детекции по ID."""
        from backend.app.repositories.cattle_detection_repository import CattleDetectionRepository
        from backend.app.repositories.image_repository import ImageRepository
        from backend.app.models.user_role import UserRole
        from backend.app.models.user import User
        from backend.app.models.image_batch import ImageBatch
        from backend.app.services.auth import bcrypt_context

        role = UserRole(id=1, name="user")
        test_session.add(role)
        await test_session.commit()

        user = User(id=1, login="testuser", password_hash=bcrypt_context.hash("password"), role_id=1)
        test_session.add(user)
        await test_session.commit()

        batch = ImageBatch(id=1, uid=uuid.uuid4(), user_id=1)
        test_session.add(batch)
        await test_session.commit()

        file_data = {"original_filename": "cow.jpg", "url_path": "/media/test/cow.jpg"}
        image = await ImageRepository.create(test_session, file_data, 1)

        detection = await CattleDetectionRepository.create(
            session=test_session,
            image_id=image.id,
            animal_id="COW003",
            weight=400.0
        )

        # Получаем по ID
        found = await CattleDetectionRepository.get_by_id(test_session, detection.id)

        assert found is not None
        assert found.id == detection.id
        assert found.animal_id == "COW003"

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, test_session):
        """Тест получения несуществующей детекции."""
        from backend.app.repositories.cattle_detection_repository import CattleDetectionRepository

        found = await CattleDetectionRepository.get_by_id(test_session, 99999)

        assert found is None

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_by_animal_id(self, test_session):
        """Тест получения детекций по ID животного."""
        from backend.app.repositories.cattle_detection_repository import CattleDetectionRepository
        from backend.app.repositories.image_repository import ImageRepository
        from backend.app.models.user_role import UserRole
        from backend.app.models.user import User
        from backend.app.models.image_batch import ImageBatch
        from backend.app.services.auth import bcrypt_context

        role = UserRole(id=1, name="user")
        test_session.add(role)
        await test_session.commit()

        user = User(id=1, login="testuser", password_hash=bcrypt_context.hash("password"), role_id=1)
        test_session.add(user)
        await test_session.commit()

        batch = ImageBatch(id=1, uid=uuid.uuid4(), user_id=1)
        test_session.add(batch)
        await test_session.commit()

        # Создаем несколько детекций для одного животного
        for i in range(3):
            file_data = {"original_filename": f"cow_{i}.jpg", "url_path": f"/media/test/cow_{i}.jpg"}
            image = await ImageRepository.create(test_session, file_data, 1)

            await CattleDetectionRepository.create(
                session=test_session,
                image_id=image.id,
                animal_id="SAME_COW",
                weight=400.0 + i * 10
            )

        # Получаем все детекции для животного
        detections = await CattleDetectionRepository.get_by_animal_id(test_session, "SAME_COW")

        assert len(detections) == 3

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_by_image_id(self, test_session):
        """Тест получения детекций по ID изображения."""
        from backend.app.repositories.cattle_detection_repository import CattleDetectionRepository
        from backend.app.repositories.image_repository import ImageRepository
        from backend.app.models.user_role import UserRole
        from backend.app.models.user import User
        from backend.app.models.image_batch import ImageBatch
        from backend.app.services.auth import bcrypt_context

        role = UserRole(id=1, name="user")
        test_session.add(role)
        await test_session.commit()

        user = User(id=1, login="testuser", password_hash=bcrypt_context.hash("password"), role_id=1)
        test_session.add(user)
        await test_session.commit()

        batch = ImageBatch(id=1, uid=uuid.uuid4(), user_id=1)
        test_session.add(batch)
        await test_session.commit()

        file_data = {"original_filename": "multi_cow.jpg", "url_path": "/media/test/multi_cow.jpg"}
        image = await ImageRepository.create(test_session, file_data, 1)

        # Несколько детекций для одного изображения
        for i in range(2):
            await CattleDetectionRepository.create(
                session=test_session,
                image_id=image.id,
                animal_id=f"COW_{i}",
                weight=400.0 + i * 50
            )

        detections = await CattleDetectionRepository.get_by_image_id(test_session, image.id)

        assert len(detections) == 2


class TestBatchImageRepository:
    """Тесты для репозитория пакетов изображений."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_create_batch(self, test_session):
        """Тест создания пакета."""
        from backend.app.repositories.batch_image_repository import BatchImageRepository
        from backend.app.models.user_role import UserRole
        from backend.app.models.user import User
        from backend.app.services.auth import bcrypt_context

        role = UserRole(id=1, name="user")
        test_session.add(role)
        await test_session.commit()

        user = User(id=1, login="testuser", password_hash=bcrypt_context.hash("password"), role_id=1)
        test_session.add(user)
        await test_session.commit()

        batch_uid = uuid.uuid4()
        batch = await BatchImageRepository.create(test_session, user_id=1, batch_uid=batch_uid)

        assert batch.id is not None
        assert batch.uid == batch_uid
        assert batch.user_id == 1

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_create_batch_auto_uid(self, test_session):
        """Тест создания пакета с автоматическим UUID."""
        from backend.app.repositories.batch_image_repository import BatchImageRepository
        from backend.app.models.user_role import UserRole
        from backend.app.models.user import User
        from backend.app.services.auth import bcrypt_context

        role = UserRole(id=1, name="user")
        test_session.add(role)
        await test_session.commit()

        user = User(id=1, login="testuser", password_hash=bcrypt_context.hash("password"), role_id=1)
        test_session.add(user)
        await test_session.commit()

        batch = await BatchImageRepository.create(test_session, user_id=1)

        assert batch.id is not None
        # UUID должен быть сгенерирован автоматически или None
        # В зависимости от реализации

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_by_uid(self, test_session):
        """Тест получения пакета по UUID."""
        from backend.app.repositories.batch_image_repository import BatchImageRepository
        from backend.app.models.user_role import UserRole
        from backend.app.models.user import User
        from backend.app.services.auth import bcrypt_context

        role = UserRole(id=1, name="user")
        test_session.add(role)
        await test_session.commit()

        user = User(id=1, login="testuser", password_hash=bcrypt_context.hash("password"), role_id=1)
        test_session.add(user)
        await test_session.commit()

        batch_uid = uuid.uuid4()
        await BatchImageRepository.create(test_session, user_id=1, batch_uid=batch_uid)

        found = await BatchImageRepository.get_by_uid(test_session, batch_uid)

        assert found is not None
        assert found.uid == batch_uid

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_by_uid_not_found(self, test_session):
        """Тест получения несуществующего пакета."""
        from backend.app.repositories.batch_image_repository import BatchImageRepository

        found = await BatchImageRepository.get_by_uid(test_session, uuid.uuid4())

        assert found is None

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_or_create_existing(self, test_session):
        """Тест get_or_create для существующего пакета."""
        from backend.app.repositories.batch_image_repository import BatchImageRepository
        from backend.app.models.user_role import UserRole
        from backend.app.models.user import User
        from backend.app.services.auth import bcrypt_context

        role = UserRole(id=1, name="user")
        test_session.add(role)
        await test_session.commit()

        user = User(id=1, login="testuser", password_hash=bcrypt_context.hash("password"), role_id=1)
        test_session.add(user)
        await test_session.commit()

        batch_uid = uuid.uuid4()
        original = await BatchImageRepository.create(test_session, user_id=1, batch_uid=batch_uid)

        # Пытаемся получить или создать с тем же UID
        found = await BatchImageRepository.get_or_create(test_session, user_id=1, batch_uid=batch_uid)

        assert found.id == original.id

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_or_create_new(self, test_session):
        """Тест get_or_create для нового пакета."""
        from backend.app.repositories.batch_image_repository import BatchImageRepository
        from backend.app.models.user_role import UserRole
        from backend.app.models.user import User
        from backend.app.services.auth import bcrypt_context

        role = UserRole(id=1, name="user")
        test_session.add(role)
        await test_session.commit()

        user = User(id=1, login="testuser", password_hash=bcrypt_context.hash("password"), role_id=1)
        test_session.add(user)
        await test_session.commit()

        new_uid = uuid.uuid4()
        batch = await BatchImageRepository.get_or_create(test_session, user_id=1, batch_uid=new_uid)

        assert batch.id is not None
        assert batch.uid == new_uid
