# backend/app/api/history.py
from datetime import date, datetime, time, UTC
from math import ceil
from typing import Annotated, Optional, List

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select

from backend.app.services.auth import get_current_user, db_dependency
from backend.app.models.cattle_detection import CattleDetection
from backend.app.models.image import Image
from backend.app.models.image_batch import ImageBatch
from backend.app.models.user import User as UserORM
from backend.schemas.history import HistoryItem, HistoryResponse

router = APIRouter(tags=["history"])

@router.get("history/{id}", response_model=HistoryResponse)
async def get_history_by_id(
        animal_id: str,
        db: db_dependency):
    base_query = (
        select(CattleDetection, Image, ImageBatch, UserORM)
        .join(Image, CattleDetection.image_id == Image.id)
        .join(ImageBatch, Image.batch_id == ImageBatch.id)
        .join(UserORM, ImageBatch.user_id == UserORM.id)
    )
    if animal_id is not None:
        base_query = base_query.where(CattleDetection.animal_id == str(animal_id))
    result = await db.execute(base_query)
    rows: List[tuple[CattleDetection, Image, ImageBatch, UserORM]] = result.all()

    items: list[HistoryItem] = []
    for detection, image, batch, user in rows:
        items.append(
            HistoryItem(
                id=detection.id,
                animal_id=str(detection.nn_object_id) if detection.nn_object_id is not None else None,
                weight=detection.weight,
                weight_units="kg",
                confidence=detection.confidence,  # добавишь поле в БД — маппишь сюда
                image_url=image.url_path,
                created_at=detection.create_datetime,
                created_by=user.login,
                batch_id=str(batch.uid),
            )
        )

    return HistoryResponse(
        data=items,
    )


@router.get("/history", response_model=HistoryResponse)
async def get_history(
    db: db_dependency,
    current_user: Annotated[dict, Depends(get_current_user)],
    animal_id: Optional[int] = Query(None, description="ID животного (nn_object_id)"),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
):
    # Базовый запрос: detections → images → image_batches → users
    base_query = (
        select(CattleDetection, Image, ImageBatch, UserORM)
        .join(Image, CattleDetection.image_id == Image.id)
        .join(ImageBatch, Image.batch_id == ImageBatch.id)
        .join(UserORM, ImageBatch.user_id == UserORM.id)
    )

    # Фильтр по animal_id (nn_object_id)
    if animal_id is not None:
        base_query = base_query.where(CattleDetection.animal_id == str(animal_id))

    # Фильтр по дате (по create_datetime из cattle_detections)
    if start_date is not None:
        start_dt = datetime.combine(start_date, time.min, tzinfo=UTC)
        base_query = base_query.where(CattleDetection.create_datetime >= start_dt)

    if end_date is not None:
        end_dt = datetime.combine(end_date, time.max, tzinfo=UTC)
        base_query = base_query.where(CattleDetection.create_datetime <= end_dt)

    # Подсчёт общего количества записей
    count_subq = base_query.with_only_columns(CattleDetection.id).subquery()
    total_result = await db.execute(select(func.count()).select_from(count_subq))
    total: int = total_result.scalar_one() or 0

    # Пагинация
    offset = (page - 1) * limit
    query = (
        base_query
        .order_by(CattleDetection.create_datetime.desc())
        .offset(offset)
        .limit(limit)
    )

    result = await db.execute(query)
    rows: List[tuple[CattleDetection, Image, ImageBatch, UserORM]] = result.all()

    items: list[HistoryItem] = []
    for detection, image, batch, user in rows:
        items.append(
            HistoryItem(
                id=detection.id,
                animal_id=str(detection.nn_object_id) if detection.nn_object_id is not None else None,
                weight=detection.weight,
                weight_units="kg",
                confidence=detection.confidence,              # добавишь поле в БД — маппишь сюда
                image_url=image.url_path,
                created_at=detection.create_datetime,
                created_by=user.login,
                batch_id=str(batch.uid),
            )
        )

    total_pages = ceil(total / limit) if total > 0 else 0

    return HistoryResponse(
        page=page,
        limit=limit,
        total=total,
        total_pages=total_pages,
        data=items,
    )
