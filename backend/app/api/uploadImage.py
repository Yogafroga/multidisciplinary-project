import uuid
from fastapi import APIRouter, UploadFile, File, Form, status, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.services.image_service import image_service
from backend.app.services.auth import get_current_user
from backend.app.utils.validators import image_validator
from backend.app.database import get_db
from backend.schemas.upload import UploadImagesResponse, FileUploadResult

router = APIRouter(tags=['Upload'])


@router.post("/upload_images", status_code=status.HTTP_201_CREATED, response_model=UploadImagesResponse)
async def upload_image(
    file: UploadFile = File(..., description="Файл изображения (jpg, png)"),
    animal_id: str = Form(..., description="Идентификатор животного (номер бирки)"),
    session: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> UploadImagesResponse:
    """
    Загрузка изображения для взвешивания.
    
    Сохраняет файл в хранилище (S3 или локально), создаёт запись в БД
    и запись детекции с предсказанным весом.
    
    **Form-data параметры:**
    - file: файл изображения (jpg, png)
    - animal_id: строка — идентификатор животного (номер бирки), обязательный
    
    **Заголовки:**
    - Authorization: Bearer <token>
    - Content-Type: multipart/form-data
    """
    batch_id = str(uuid.uuid4())
    user_id = current_user['user_id']
    
    file_result = FileUploadResult(
        filename=file.filename,
        status="pending"
    )

    try:
        # Валидация файла
        validated_file = await image_validator.validate(file)

        # Сохранение (на диск/S3 + в БД) и создание детекции
        image, detection = await image_service.upload_image(
            file=validated_file,
            subfolder_name=batch_id,
            user_id=user_id,
            session=session,
            animal_id=animal_id
        )

        file_result = FileUploadResult(
            filename=file.filename,
            status="success",
            image_id=image.id,
            image_url=image.url_path,
            animal_id=animal_id,
            weight=detection.weight
        )

    except HTTPException as e:
        # Ошибки валидации (400, 413)
        file_result = FileUploadResult(
            filename=file.filename,
            status="failed",
            error=e.detail
        )
    except Exception as e:
        # Непредвиденные ошибки
        file_result = FileUploadResult(
            filename=file.filename,
            status="error",
            error=f"Internal processing error: {str(e)}"
        )

    return UploadImagesResponse(
        batch_id=batch_id,
        files=[file_result]
    )

