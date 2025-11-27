from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.models.image_batch import ImageBatch
import uuid


class BatchImageRepository:

    @staticmethod
    async def create(session: AsyncSession, user_id: int, batch_uid: Optional[uuid.UUID] = None) -> ImageBatch:
        """Создать новый батч"""
        batch = ImageBatch(
            user_id=user_id,
            uid=batch_uid
        )

        session.add(batch)
        await session.commit()
        await session.refresh(batch)

        return batch

    @staticmethod
    async def get_by_uid(session: AsyncSession, uid: uuid.UUID) -> Optional[ImageBatch]:
        """Получить батч по UUID"""
        result = await session.execute(
            select(ImageBatch).where(ImageBatch.uid == uid)
        )
        return result.scalar_one_or_none()


batch_image_repository = BatchImageRepository()
