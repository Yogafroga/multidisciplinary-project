# backend/app/api/history.py
from datetime import date, datetime, time, UTC
from http.client import HTTPException
from math import ceil
from typing import Annotated, Optional, List

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy import func, select, delete

from backend.app.services.auth import get_current_user, db_dependency
from backend.app.models.cattle_detection import CattleDetection
from backend.app.models.image import Image
from backend.app.models.image_batch import ImageBatch
from backend.app.models.user import User as UserORM
from backend.schemas.history import HistoryItem, HistoryResponse, DeleteHistoryResponse

router = APIRouter(tags=["history"])

@router.delete("/history/{id}", response_model=DeleteHistoryResponse)
async def delete_history(id: int, db: db_dependency):
    base_query = (
        delete(CattleDetection).where(CattleDetection.id == id)
    )
    result = await db.execute(base_query)
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="History not found")
    await db.commit()

    return DeleteHistoryResponse(
        message="Record deleted successfully"
    )

@router.get("/history/{animal_id}", response_model=HistoryItem)
async def get_history_by_id(
        animal_id: str,
        db: db_dependency):
    base_query = (
        select(CattleDetection, Image, ImageBatch, UserORM)
        .join(Image, CattleDetection.image_id == Image.id)
        .join(ImageBatch, Image.batch_id == ImageBatch.id)
        .join(UserORM, ImageBatch.user_id == UserORM.id)
        .where(CattleDetection.animal_id == str(animal_id))
    )

    result = await db.execute(base_query)
    rows: List[tuple[CattleDetection, Image, ImageBatch, UserORM]] = result.all()

    # Проверка на пустой результат
    if not rows:
        raise HTTPException(status_code=404, detail="History not found")

    # Распаковка первого элемента
    detection, image, batch, user = rows[0]

    # Правильное создание модели
    return HistoryItem(
        id=detection.id,
        animal_id=detection.animal_id,
        weight=detection.weight,
        weight_units="kg",
        confidence=detection.confidence,
        image_url=image.url_path,
        created_at=detection.create_datetime,
        created_by=user.login,
        batch_id=str(batch.uid),
    )


@router.get("/history", response_model=HistoryResponse)
async def get_history(
        db: db_dependency,
        current_user: Annotated[dict, Depends(get_current_user)],
        animal_id: Optional[str] = Query(None, description="ID животного (номер бирки)"),
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

    # Фильтр по animal_id (номер бирки)
    if animal_id is not None:
        base_query = base_query.where(CattleDetection.animal_id == animal_id)

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
                animal_id=detection.animal_id,
                weight=detection.weight,
                weight_units="kg",
                confidence=detection.confidence,  # добавишь поле в БД — маппишь сюда
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
