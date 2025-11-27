from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.helpers.file_helper import save_file
from backend.app.repositories.image_repository import image_repository
from backend.app.models.weighing import Weighing


class ImageService:
    """Сервис для управления загрузкой изображений"""

    async def upload_image(self, file: UploadFile, subfolder_name: str, session: AsyncSession) -> Weighing:
        """
        Загружает изображение: сохраняет на диск и в БД.

        ВРЕМЕННОЕ РЕШЕНИЕ (КОСТЫЛЬ): сохраняет в таблицу weighings с заглушками.
        TODO: После создания таблицы images - переделать.

        Args:
            file: Загруженный файл
            subfolder_name: Имя подпапки для сохранения (например, UUID батча)
            session: Асинхронная сессия БД

        Returns:
            Weighing: Созданная запись о взвешивании с путём к изображению

        Raises:
            OSError: При ошибке сохранения файла на диск
        """
        # 1. Сохраняем файл на диск
        file_data = await save_file(file, subfolder_name)

        # 2. Сохраняем информацию о файле в БД (временно в weighings)
        weighing = await image_repository.create(session, file_data)

        return weighing


image_service = ImageService()