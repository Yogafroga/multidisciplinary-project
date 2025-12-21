# backend/app/api/batches.py
from datetime import datetime
from typing import List, Annotated
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from backend.app.database import get_db
from backend.app.models.image_batch import ImageBatch
from backend.app.models.image import Image
from backend.app.models.cattle_detection import CattleDetection
from backend.app.services.auth import get_current_user
from backend.schemas.batches import BatchStatsResponse

router = APIRouter(prefix="/batches", tags=["batches"])


@router.get("/stats", response_model=BatchStatsResponse)
async def get_batch_statistics(
        current_user: Annotated[dict, Depends(get_current_user)],
        page: int = Query(1, ge=1, description="Номер страницы (начиная с 1)"),
        limit: int = Query(10, ge=1, le=100, description="Количество записей на странице"),
        db: AsyncSession = Depends(get_db),
):
    """
    GET /batches/stats?page=1&limit=10 - статистика по батчам с пагинацией
    """
    # Подсчет общего количества батчей
    count_query = select(func.count(ImageBatch.id))
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Основной запрос с пагинацией
    offset = (page - 1) * limit

    query = (
        select(
            ImageBatch.id.label("batch_number"),
            func.count(Image.id).label("photo_count"),
            func.avg(CattleDetection.weight).label("avg_weight"),
            func.coalesce(func.sum(CattleDetection.weight), 0).label("total_weight"),
            func.to_char(ImageBatch.create_datetime, 'YYYY-MM-DD').label("create_date"),
            func.to_char(ImageBatch.create_datetime, 'HH24:MI:SS').label("create_time"),
        )
        .outerjoin(Image, Image.batch_id == ImageBatch.id)
        .outerjoin(CattleDetection, CattleDetection.image_id == Image.id)
        .group_by(ImageBatch.id, ImageBatch.create_datetime)
        .order_by(ImageBatch.create_datetime.desc())
        .offset(offset)
        .limit(limit)
    )

    result = await db.execute(query)
    rows = result.all()

    stats = []
    for row in rows:
        stats.append({
            "batch_number": row.batch_number,
            "photo_count": row.photo_count,
            "avg_weight": row.avg_weight,
            "total_weight": float(row.total_weight),
            "create_date": row.create_date,
            "create_time": row.create_time,
        })

    total_pages = (total + limit - 1) // limit  # ceiling division

    return BatchStatsResponse(
        items=stats,
        total=total,
        page=page,
        limit=limit,
        total_pages=total_pages
    )
