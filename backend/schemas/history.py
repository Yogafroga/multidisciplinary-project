# backend/app/schemas/history.py
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class HistoryItem(BaseModel):
    id: int
    animal_id: Optional[str] = None
    weight: Optional[float] = None
    weight_units: str
    confidence: Optional[float] = None
    original_name: str
    created_at: datetime
    created_by: str
    batch_id: str


class HistoryResponse(BaseModel):
    page: int
    limit: int
    total: int
    total_pages: int
    data: List[HistoryItem]

class DeleteHistoryResponse(BaseModel):
    message: str