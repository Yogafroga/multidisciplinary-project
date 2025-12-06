import uuid
from fastapi import APIRouter, UploadFile, File, status, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.services.archive_service import archive_service
from backend.app.services.auth import get_current_user
from backend.app.database import get_db
from backend.schemas.upload import UploadArchiveResponse, ArchiveSummary, ArchiveFileDetail

router = APIRouter(tags=['Upload'])


@router.post("/upload_archive", status_code=status.HTTP_201_CREATED, response_model=UploadArchiveResponse)
async def upload_archive(
    file: UploadFile = File(..., description="ZIP-архив с изображениями"),
    session: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> UploadArchiveResponse:
    """
    Загрузка ZIP-архива с изображениями для массового взвешивания.
    
    Система автоматически:
    - Распаковывает архив
    - Обрабатывает все изображения
    - Определяет вес каждого животного
    - Формирует сводный отчёт
    
    ID животного извлекается из имени файла (например: cow_001.jpg -> 001)
    
    **Form-data параметры:**
    - file: ZIP-архив с изображениями (jpg, png)
    
    **Заголовки:**
    - Authorization: Bearer <token>
    - Content-Type: multipart/form-data
    """
    # Проверяем, что это ZIP-архив
    if not file.filename.lower().endswith('.zip'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Файл должен быть ZIP-архивом"
        )
    
    archive_id = str(uuid.uuid4())
    user_id = current_user['user_id']
    
    try:
        # Обрабатываем архив
        successful, failed = await archive_service.process_archive(
            file=file,
            batch_id=archive_id,
            user_id=user_id,
            session=session
        )
        
        # Рассчитываем сводку
        summary_data = archive_service.calculate_summary(successful)
        
        # Формируем детали по каждому файлу
        details = []
        for item in successful:
            details.append(ArchiveFileDetail(
                filename=item["filename"],
                status=item["status"],
                image_id=item.get("image_id"),
                image_url=item.get("image_url"),
                weight=item.get("weight"),
                confidence=item.get("confidence")
            ))
        
        for item in failed:
            details.append(ArchiveFileDetail(
                filename=item["filename"],
                status=item["status"],
                error=item.get("error")
            ))
        
        return UploadArchiveResponse(
            archive_id=archive_id,
            total_images=len(successful) + len(failed),
            processed_images=len(successful),
            failed_images=len(failed),
            summary=ArchiveSummary(**summary_data),
            details=details
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка обработки архива: {str(e)}"
        )