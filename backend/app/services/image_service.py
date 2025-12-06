from typing import Tuple, Optional
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
import random # Для заглушки веса

from backend.app.helpers.file_helper import save_file_to_s3, save_file_to_folder
from backend.app.models.image import Image
from backend.app.models.cattle_detection import CattleDetection
from backend.app.repositories.image_repository import image_repository
from backend.app.repositories.batch_image_repository import batch_image_repository
from backend.app.repositories.cattle_detection_repository import cattle_detection_repository
from backend.app.core.config import settings


class ImageService:
    """Сервис для управления и сохранения информации о изображениях"""

    async def process_file_upload(self, file: UploadFile, subfolder_name: str, s3_client=None) -> dict:
        """
        Только загружает файл в хранилище. Не трогает БД.
        """
        if all([
            settings.VK_S3_ENDPOINT_URL,
            settings.VK_S3_BUCKET_NAME,
            settings.VK_S3_ACCESS_KEY_ID,
            settings.VK_S3_SECRET_KEY
        ]):
            file_data = await save_file_to_s3(file, subfolder_name, s3_client=s3_client)
            file_data["url_path"] = file_data["url"]
        else:
            file_data = await save_file_to_folder(file, subfolder_name)
            file_data["url_path"] = f"/media/{subfolder_name}/{file_data['filename']}"
            
        return file_data

    async def create_db_entries(
        self, 
        session: AsyncSession, 
        file_data: dict, 
        batch_id: int, 
        animal_id: str
    ) -> Tuple[Image, CattleDetection]:
        """
        Создает записи в БД на основе уже загруженного файла.
        """
        image = await image_repository.create(session, file_data, batch_id)
        
        predicted_weight = await self._predict_weight(file_data["url_path"])
        #TODO:Заменить на реальный вызов предсказания веса
        detection = await cattle_detection_repository.create(
            session=session,
            image_id=image.id,
            animal_id=animal_id,
            weight=predicted_weight,
            confidence=0.85 #TODO:Заглушка для предсказания веса.
        )
        return image, detection

    # Старый метод для обратной совместимости (для одиночной загрузки)
    async def upload_image(
        self,
        file: UploadFile,
        subfolder_name: str,
        user_id: int,
        session: AsyncSession,
        animal_id: str
    ) -> Tuple[Image, CattleDetection]:
        
        batch_uuid = uuid.UUID(subfolder_name)
        batch = await batch_image_repository.get_or_create(session, user_id, batch_uuid)
        
        file_data = await self.process_file_upload(file, subfolder_name)
        return await self.create_db_entries(session, file_data, batch.id, animal_id)

    async def _predict_weight(self, image_path: str) -> float:
        """
        Заглушка для предсказания веса.
        
        TODO: Заменить на реальный вызов ML-модели.
        """
        import random
        return round(random.uniform(400.0, 550.0), 1)


image_service = ImageService()