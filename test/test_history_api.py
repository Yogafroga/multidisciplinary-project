"""
Тесты для API истории взвешиваний (/api/history).

Покрывает:
- Получение списка истории
- Получение истории по ID животного
- Удаление записи истории
- Пагинация и фильтрация
"""
import pytest
from datetime import datetime, UTC
from unittest.mock import AsyncMock, patch
from fastapi import status
import uuid


class TestHistoryAPI:
    """Тесты для эндпоинтов истории взвешиваний."""

    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_get_history_empty(self, async_client, test_session, auth_headers):
        """Тест получения пустой истории."""
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

        response = await async_client.get("/api/history", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 0
        assert data["data"] == []
        assert data["page"] == 1

    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_get_history_with_data(self, async_client, test_session, auth_headers):
        """Тест получения истории с данными."""
        from backend.app.models.user_role import UserRole
        from backend.app.models.user import User
        from backend.app.models.image_batch import ImageBatch
        from backend.app.models.image import Image
        from backend.app.models.cattle_detection import CattleDetection
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

        # Создаем батч
        batch = ImageBatch(
            id=1,
            uid=uuid.uuid4(),
            user_id=1
        )
        test_session.add(batch)
        await test_session.commit()

        # Создаем изображение
        image = Image(
            id=1,
            uid=uuid.uuid4(),
            url_path="/media/test/image.jpg",
            batch_id=1
        )
        test_session.add(image)
        await test_session.commit()

        # Создаем детекцию
        detection = CattleDetection(
            id=1,
            animal_id="001",
            weight=450.5,
            confidence=0.95,
            image_id=1
        )
        test_session.add(detection)
        await test_session.commit()

        response = await async_client.get("/api/history", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 1
        assert len(data["data"]) == 1
        assert data["data"][0]["animal_id"] == "001"
        assert data["data"][0]["weight"] == 450.5

    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_get_history_pagination(self, async_client, test_session, auth_headers):
        """Тест пагинации истории."""
        from backend.app.models.user_role import UserRole
        from backend.app.models.user import User
        from backend.app.models.image_batch import ImageBatch
        from backend.app.models.image import Image
        from backend.app.models.cattle_detection import CattleDetection
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

        # Создаем батч
        batch = ImageBatch(id=1, uid=uuid.uuid4(), user_id=1)
        test_session.add(batch)
        await test_session.commit()

        # Создаем 25 записей
        for i in range(25):
            image = Image(
                id=i + 1,
                uid=uuid.uuid4(),
                url_path=f"/media/test/image_{i}.jpg",
                batch_id=1
            )
            test_session.add(image)
            await test_session.commit()

            detection = CattleDetection(
                id=i + 1,
                animal_id=f"{i+1:03d}",
                weight=400.0 + i,
                confidence=0.9,
                image_id=i + 1
            )
            test_session.add(detection)
            await test_session.commit()

        # Первая страница
        response = await async_client.get(
            "/api/history?page=1&limit=10",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 25
        assert len(data["data"]) == 10
        assert data["page"] == 1
        assert data["total_pages"] == 3

        # Вторая страница
        response = await async_client.get(
            "/api/history?page=2&limit=10",
            headers=auth_headers
        )
        data = response.json()
        assert len(data["data"]) == 10
        assert data["page"] == 2

    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_get_history_filter_by_animal_id(self, async_client, test_session, auth_headers):
        """Тест фильтрации по ID животного."""
        from backend.app.models.user_role import UserRole
        from backend.app.models.user import User
        from backend.app.models.image_batch import ImageBatch
        from backend.app.models.image import Image
        from backend.app.models.cattle_detection import CattleDetection
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

        # Создаем батч
        batch = ImageBatch(id=1, uid=uuid.uuid4(), user_id=1)
        test_session.add(batch)
        await test_session.commit()

        # Создаем записи для разных животных
        for i, animal_id in enumerate(["001", "001", "002"]):
            image = Image(
                id=i + 1,
                uid=uuid.uuid4(),
                url_path=f"/media/test/image_{i}.jpg",
                batch_id=1
            )
            test_session.add(image)
            await test_session.commit()

            detection = CattleDetection(
                id=i + 1,
                animal_id=animal_id,
                weight=400.0 + i * 10,
                confidence=0.9,
                image_id=i + 1
            )
            test_session.add(detection)
            await test_session.commit()

        # Фильтруем по animal_id=001
        response = await async_client.get(
            "/api/history?animal_id=001",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 2
        assert all(item["animal_id"] == "001" for item in data["data"])

    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_get_history_by_id_success(self, async_client, test_session):
        """Тест получения истории по ID животного."""
        from backend.app.models.user_role import UserRole
        from backend.app.models.user import User
        from backend.app.models.image_batch import ImageBatch
        from backend.app.models.image import Image
        from backend.app.models.cattle_detection import CattleDetection
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

        # Создаем батч
        batch = ImageBatch(id=1, uid=uuid.uuid4(), user_id=1)
        test_session.add(batch)
        await test_session.commit()

        # Создаем изображение и детекцию
        image = Image(
            id=1,
            uid=uuid.uuid4(),
            url_path="/media/test/image.jpg",
            batch_id=1
        )
        test_session.add(image)
        await test_session.commit()

        detection = CattleDetection(
            id=1,
            animal_id="COW123",
            weight=500.0,
            confidence=0.98,
            image_id=1
        )
        test_session.add(detection)
        await test_session.commit()

        response = await async_client.get("/api/history/COW123")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["animal_id"] == "COW123"
        assert data["weight"] == 500.0

    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_get_history_by_id_not_found(self, async_client, test_session):
        """Тест получения несуществующей записи истории."""
        response = await async_client.get("/api/history/NONEXISTENT")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_delete_history_success(self, async_client, test_session):
        """Тест успешного удаления записи истории."""
        from backend.app.models.user_role import UserRole
        from backend.app.models.user import User
        from backend.app.models.image_batch import ImageBatch
        from backend.app.models.image import Image
        from backend.app.models.cattle_detection import CattleDetection
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

        # Создаем батч
        batch = ImageBatch(id=1, uid=uuid.uuid4(), user_id=1)
        test_session.add(batch)
        await test_session.commit()

        # Создаем изображение и детекцию
        image = Image(
            id=1,
            uid=uuid.uuid4(),
            url_path="/media/test/image.jpg",
            batch_id=1
        )
        test_session.add(image)
        await test_session.commit()

        detection = CattleDetection(
            id=1,
            animal_id="DELETE001",
            weight=450.0,
            confidence=0.9,
            image_id=1
        )
        test_session.add(detection)
        await test_session.commit()

        response = await async_client.delete("/api/history/1")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["message"] == "Record deleted successfully"

    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_delete_history_not_found(self, async_client, test_session):
        """Тест удаления несуществующей записи."""
        response = await async_client.delete("/api/history/99999")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_get_history_unauthorized(self, async_client):
        """Тест доступа к истории без авторизации."""
        response = await async_client.get("/api/history")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
