from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from backend.app.helpers.file_helper import save_file_to_s3, save_file_to_folder
from backend.app.models.image import Image
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
        file_data["url_path"] = file_data["url"]  # Используем полный URL S3
    else:
        # Используем локальное сохранение, если S3 не настроен
        file_data = await save_file_to_folder(file, subfolder_name)
        # Формируем относительный URL для локального файла
        file_data["url_path"] = f"/media/{subfolder_name}/{file_data['filename']}"

    # 4. Сохраняем информацию о файле в БД
    image = await image_repository.create(session, file_data, batch.id)

    return image


image_service = ImageService()