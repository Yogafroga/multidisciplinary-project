from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.models.cattle_detection import CattleDetection


class CattleDetectionRepository:
    """Репозиторий для работы с детекциями скота в БД"""

    @staticmethod
    async def create(
        session: AsyncSession,
        image_id: int,
        animal_id: str,
        weight: Optional[float] = None,
        confidence: Optional[float] = None,
        nn_object_id: Optional[int] = None
    ) -> CattleDetection:
        detection = CattleDetection(
            image_id=image_id,
            animal_id=animal_id,
            weight=weight,
            confidence=confidence,
            nn_object_id=nn_object_id
        )

        session.add(detection)
        await session.commit()
        await session.refresh(detection)

        return detection

    @staticmethod
    async def get_by_id(session: AsyncSession, detection_id: int) -> Optional[CattleDetection]:
        result = await session.execute(
            select(CattleDetection).where(CattleDetection.id == detection_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_image_id(session: AsyncSession, image_id: int) -> List[CattleDetection]:
        result = await session.execute(
            select(CattleDetection).where(CattleDetection.image_id == image_id)
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_by_animal_id(session: AsyncSession, animal_id: str) -> List[CattleDetection]:
        result = await session.execute(
            select(CattleDetection).where(CattleDetection.animal_id == animal_id)
        )
        return list(result.scalars().all())


cattle_detection_repository = CattleDetectionRepository()