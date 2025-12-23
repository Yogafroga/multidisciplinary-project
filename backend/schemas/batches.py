from pydantic import BaseModel
from typing import List


class BatchStats(BaseModel):
    batch_number: int
    photo_count: int
    avg_weight: float | None
    total_weight: float
    detection_ids: List[int]  # Список ID детекций коров
    create_date: str
    create_time: str


class BatchStatsResponse(BaseModel):
    items: List[BatchStats]
    total: int
    page: int
    limit: int
    total_pages: int
