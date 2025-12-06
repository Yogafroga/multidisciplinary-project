from pydantic import BaseModel
from typing import Optional, List


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

