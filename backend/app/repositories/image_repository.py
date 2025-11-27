from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.models.weighing import Weighing


class ImageRepository:
    """Репозиторий для работы с изображениями в БД"""

    @staticmethod
    async def create(session: AsyncSession, file_data: dict) -> Weighing:
        """
        ВРЕМЕННОЕ РЕШЕНИЕ (КОСТЫЛЬ):
        Создает запись в weighings с заглушками для animal_id и predicted_weight.

        TODO: Создать отдельную таблицу images и использовать её.

        Args:
            session: Асинхронная сессия БД
            file_data: Словарь с данными о файле (должен содержать "file_path")

        Returns:
            Weighing: Созданная запись о взвешивании с путём к изображению
        """
        # КОСТЫЛЬ: используем заглушки для обязательных полей
        weighing = Weighing(
            animal_id=1,  # TODO: заглушка, нужно реальное животное
            predicted_weight=0.0,  # TODO: заглушка, нужен реальный вес
            image_url=file_data["file_path"]
        )

        session.add(weighing)
        await session.commit()
        await session.refresh(weighing)

        return weighing


# Создаем экземпляр репозитория
image_repository = ImageRepository()
