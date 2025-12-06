from typing import Tuple
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from backend.app.helpers.file_helper import save_file_to_s3, save_file_to_folder
from backend.app.models.image import Image
from backend.app.models.cattle_detection import CattleDetection
from backend.app.repositories.image_repository import image_repository
from backend.app.repositories.batch_image_repository import batch_image_repository
from backend.app.repositories.cattle_detection_repository import cattle_detection_repository


class ImageService:
    """Сервис для управления и сохранения информации о изображениях"""

    async def upload_image(
        self,
        file: UploadFile,
        subfolder_name: str,
        user_id: int,
        session: AsyncSession,
        animal_id: str
    ) -> Tuple[Image, CattleDetection]:
        """
        Загрузка и сохранение изображения с созданием записи детекции.

        Args:
            file: Загруженный файл
            subfolder_name: UUID батча в виде строки (название папки)
            user_id: ID пользователя, загружающего файл
            session: Сессия БД
            animal_id: Идентификатор животного (номер бирки)

        Returns:
            Tuple[Image, CattleDetection]: Созданные объекты
        """
        # 1. Преобразуем subfolder_name (UUID строка) в UUID объект
        batch_uuid = uuid.UUID(subfolder_name)

        # 2. Создаем новый батч
        batch = await batch_image_repository.create(session, user_id, batch_uuid)

        # 3. Проверяем наличие настроек S3
        from backend.app.core.config import settings
        
        if all([
            settings.VK_S3_ENDPOINT_URL,
            settings.VK_S3_BUCKET_NAME,
            settings.VK_S3_ACCESS_KEY_ID,
            settings.VK_S3_SECRET_KEY
        ]):
            # Используем S3, если все настройки заданы
            file_data = await save_file_to_s3(file, subfolder_name)
            file_data["url_path"] = file_data["url"]
        else:
            # Используем локальное сохранение, если S3 не настроен
            file_data = await save_file_to_folder(file, subfolder_name)
            file_data["url_path"] = f"/media/{subfolder_name}/{file_data['filename']}"

        # 4. Сохраняем информацию о файле в БД
        image = await image_repository.create(session, file_data, batch.id)

        # 5. Создаём запись детекции с предсказанным весом
        # TODO: Здесь будет вызов ML-модели для получения веса
        predicted_weight = await self._predict_weight(file_data["url_path"])
        
        detection = await cattle_detection_repository.create(
            session=session,
            image_id=image.id,
            animal_id=animal_id,
            weight=predicted_weight,
            confidence=0.85  # TODO: получать от ML-модели
        )

        return image, detection

    async def _predict_weight(self, image_path: str) -> float:
        """
        Заглушка для предсказания веса.
        
        TODO: Заменить на реальный вызов ML-модели.
        
        Args:
            image_path: Путь к изображению
            
        Returns:
            float: Предсказанный вес в кг
        """
        # Заглушка: возвращаем случайный вес в диапазоне 400-550 кг
        import random
        return round(random.uniform(400.0, 550.0), 1)


image_service = ImageService()

