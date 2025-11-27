from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from backend.app.models.image import Image
from backend.app.helpers.file_helper import save_file
from backend.app.repositories.image_repository import image_repository
from backend.app.repositories.batch_image_repository import batch_image_repository


class ImageService:
    """Сервис для управления и сохранения информации о изображениях"""

    async def upload_image(
        self,
        file: UploadFile,
        subfolder_name: str,
        user_id: int,
        session: AsyncSession
    ) -> Image:
        """
        Загрузка и сохранение изображения.

        Args:
            file: Загруженный файл
            subfolder_name: UUID батча в виде строки (название папки)
            user_id: ID пользователя, загружающего файл
            session: Сессия БД

        Returns:
            Image: Созданный объект изображения
        """
        # 1. Преобразуем subfolder_name (UUID строка) в UUID объект
        batch_uuid = uuid.UUID(subfolder_name)

        # 2. Создаем новый батч (UUID уникален, проверка не нужна)
        batch = await batch_image_repository.create(session, user_id, batch_uuid)

        # 3. Сохраняем файл на диск
        file_data = await save_file(file, subfolder_name)

        # 4. Сохраняем информацию о файле в БД с batch_db_id
        image = await image_repository.create(session, file_data, batch.id)

        return image


image_service = ImageService()