from typing import List

from pydantic import BaseModel


class BatchStats(BaseModel):
    batch_number: int
    photo_count: int
    avg_weight: float | None
    total_weight: float | None
    create_date: str
    create_time: str


class BatchStatsResponse(BaseModel):
    items: List[BatchStats]
    total: int
    page: int
    limit: int
    total_pages: int
