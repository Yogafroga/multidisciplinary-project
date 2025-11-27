from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.models.image import Image


class ImageRepository:
    """Репозиторий для работы с изображениями в БД"""

    @staticmethod
    async def create(session: AsyncSession, file_data: dict, batch_db_id: int) -> Image:
        """
        Создает новую запись изображения в БД.

        Args:
            session: Сессия БД
            file_data: Словарь с данными файла (из save_file)
                - file_data["subfolder"] содержит batch_uid (UUID строку)
            batch_db_id: ID записи батча в БД (integer FK к image_batches.id)

        Returns:
            Image: Созданный объект изображения
        """
        image = Image(
            original_name=file_data.get("original_filename"),
            url_path=file_data.get("file_path"),
            batch_id=batch_db_id,
            status="UPLOADED"
        )

        session.add(image)
        await session.commit()
        await session.refresh(image)

        return image

    # @staticmethod
    # async def get_by_id(session: AsyncSession, image_id: int) -> Optional[Image]:
    #     """Получить изображение по ID"""
    #     result = await session.execute(
    #         select(Image).where(Image.id == image_id)
    #     )
    #     return result.scalar_one_or_none()

    # @staticmethod
    # async def get_by_uid(session: AsyncSession, uid: str) -> Optional[Image]:
    #     """Получить изображение по UUID"""
    #     result = await session.execute(
    #         select(Image).where(Image.uid == uid)
    #     )
    #     return result.scalar_one_or_none()

    # @staticmethod
    # async def get_by_batch_id(session: AsyncSession, batch_id: int) -> List[Image]:
    #     """Получить все изображения батча"""
    #     result = await session.execute(
    #         select(Image).where(Image.batch_id == batch_id)
    #     )
    #     return list(result.scalars().all())

    # @staticmethod
    # async def update_status(session: AsyncSession, image_id: int, status: str) -> Optional[Image]:
    #     """
    #     Обновить статус изображения.

    #     Args:
    #         session: Сессия БД
    #         image_id: ID изображения
    #         status: Новый статус (например: UPLOADED, PROCESSING, PROCESSED, FAILED)

    #     Returns:
    #         Image: Обновленное изображение или None
    #     """
    #     image = await ImageRepository.get_by_id(session, image_id)
    #     if image:
    #         image.status = status
    #         await session.commit()
    #         await session.refresh(image)
    #     return image

    # @staticmethod
    # async def delete(session: AsyncSession, image_id: int) -> bool:
    #     """
    #     Удалить изображение из БД.

    #     Args:
    #         session: Сессия БД
    #         image_id: ID изображения

    #     Returns:
    #         bool: True если удалено, False если не найдено
    #     """
    #     image = await ImageRepository.get_by_id(session, image_id)
    #     if image:
    #         await session.delete(image)
    #         await session.commit()
    #         return True
    #     return False

    # @staticmethod
    # async def count_by_batch(session: AsyncSession, batch_id: int) -> int:
    #     """Подсчитать количество изображений в батче"""
    #     result = await session.execute(
    #         select(Image).where(Image.batch_id == batch_id)
    #     )
    #     return len(list(result.scalars().all()))

    # @staticmethod
    # async def get_by_status(session: AsyncSession, status: str, limit: int = 100) -> List[Image]:
    #     """
    #     Получить изображения по статусу.

    #     Args:
    #         session: Сессия БД
    #         status: Статус для фильтрации
    #         limit: Максимальное количество результатов

    #     Returns:
    #         List[Image]: Список изображений
    #     """
    #     result = await session.execute(
    #         select(Image).where(Image.status == status).limit(limit)
    #     )
    #     return list(result.scalars().all())


# Создаем экземпляр репозитория
image_repository = ImageRepository()
