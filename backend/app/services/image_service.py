from typing import Tuple, Optional, Dict, Any
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
import random  # Fallback для заглушки веса

from backend.app.helpers.file_helper import save_file_to_s3, save_file_to_folder
from backend.app.models.image import Image
from backend.app.models.cattle_detection import CattleDetection
from backend.app.repositories.image_repository import image_repository
from backend.app.repositories.batch_image_repository import batch_image_repository
from backend.app.repositories.cattle_detection_repository import cattle_detection_repository
from backend.app.core.config import settings

# Ленивая инициализация ML адаптера
_cattle_adapter = None

def _get_cattle_adapter():
    """Ленивая загрузка ML модели для избежания загрузки при импорте"""
    global _cattle_adapter
    if _cattle_adapter is None and settings.ML_ENABLED:
        try:
            from backend.app.ml_service.cattle_adapter import CattleAdapter
            _cattle_adapter = CattleAdapter(
                seg_model_path=str(settings.SEG_MODEL_PATH),
                reg_model_path=str(settings.REG_MODEL_PATH)
            )
        except Exception as e:
            print(f"Warning: Failed to load ML model: {e}")
            return None
    return _cattle_adapter


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
        animal_id: str,
        image_bytes: bytes = None
    ) -> Tuple[Image, CattleDetection]:
        """
        Создает записи в БД на основе уже загруженного файла.
        image_bytes - байты изображения для ML предсказания (опционально)
        """
        image = await image_repository.create(session, file_data, batch_id)

        prediction = await self._predict_weight(image_bytes)
        detection = await cattle_detection_repository.create(
            session=session,
            image_id=image.id,
            animal_id=animal_id,
            weight=prediction["predicted_weight"],
            confidence=prediction["confidence"]
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

        # Читаем байты для ML предсказания
        image_bytes = await file.read()
        await file.seek(0)  # Сбрасываем позицию для последующей загрузки

        file_data = await self.process_file_upload(file, subfolder_name)
        return await self.create_db_entries(session, file_data, batch.id, animal_id, image_bytes=image_bytes)

    async def _predict_weight(self, image_bytes: bytes = None) -> Dict[str, Any]:
        """
        Предсказание веса КРС с использованием ML-модели.

        При недоступности модели или отсутствии байтов возвращает заглушку.

        Args:
            image_bytes: байты изображения для предсказания

        Returns:
            Dict с ключами: predicted_weight, confidence, cattle_percentage (опционально)
        """
        if image_bytes is None:
            return {"predicted_weight": 0, "confidence": 0}

        adapter = _get_cattle_adapter()

        if adapter is not None:
            try:
                result = await adapter.predict_async(image_bytes)
                return {
                    "predicted_weight": result["predicted_weight"],
                    "confidence": 0.95 if result["confidence"] == "high" else 0.65,
                    "cattle_percentage": result.get("cattle_percentage", 0)
                }
            except Exception as e:
                print(f"ML prediction failed, using fallback: {e}")

        # Fallback: заглушка
        return {
            "predicted_weight": 0,
            "confidence": 0
        }


image_service = ImageService()