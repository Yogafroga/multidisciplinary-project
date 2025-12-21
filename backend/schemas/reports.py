from datetime import date
from typing import List, Literal, Optional, Dict
from pydantic import BaseModel, Field


class ReportGenerateRequest(BaseModel):
    include_weighs: List[int]
    format: Literal["excel", "pdf"]
    animal_ids: Optional[List[str]] = Field(default=None)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    report_type: Literal["detailed", "summary"]
    include_images: bool = False


class ReportGenerateResponse(BaseModel):
    report_id: str
    status: Literal["processing", "completed", "failed"]
    estimated_time: int
    download_url: Optional[str] = None
