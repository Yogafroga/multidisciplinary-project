from pydantic import BaseModel
from typing import Optional, List


# === Схемы для одиночной загрузки ===

class FileUploadResult(BaseModel):
    """Результат загрузки одного файла"""
    filename: str
    status: str  # "success", "failed", "error"
    image_id: Optional[int] = None
    image_url: Optional[str] = None
    animal_id: Optional[str] = None
    weight: Optional[float] = None
    error: Optional[str] = None


class UploadImagesResponse(BaseModel):
    """Ответ на загрузку изображений"""
    batch_id: str
    files: List[FileUploadResult]


# === Схемы для архивной загрузки ===

class ArchiveFileDetail(BaseModel):
    """Детали обработки одного файла из архива"""
    filename: str
    status: str  # "success", "failed", "error"
    image_id: Optional[int] = None
    image_url: Optional[str] = None
    weight: Optional[float] = None
    confidence: Optional[float] = None
    error: Optional[str] = None


class ArchiveSummary(BaseModel):
    """Сводка по архиву"""
    total_weight: float
    average_weight: float
    animal_count: int
    min_weight: Optional[float] = None
    max_weight: Optional[float] = None


class UploadArchiveResponse(BaseModel):
    """Ответ на загрузку архива"""
    archive_id: str
    total_images: int
    processed_images: int
    failed_images: int
    summary: ArchiveSummary
    details: List[ArchiveFileDetail]