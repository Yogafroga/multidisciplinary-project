import uuid
from typing import List
from fastapi import APIRouter, UploadFile, File, status, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.services.image_service import image_service
from backend.app.services.auth import get_current_user
from backend.app.utils.validators import image_validator
from backend.app.database import get_db

router = APIRouter(tags=['Upload'])


@router.post("/upload_images", status_code=status.HTTP_201_CREATED)
async def upload_multiple_images(
    files: List[UploadFile] = File(...),
    session: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Массовая загрузка изображений.
    Сохраняет файлы на диск и информацию о них в БД.
    Возвращает статус по каждому файлу отдельно.
    """
    results = []
    batch_id = str(uuid.uuid4())  # Все файлы из одного запроса кладем в одну папку
    user_id = current_user['user_id']  # Получаем ID пользователя из токена

    for file in files:
        file_result = {"filename": file.filename, "status": "pending"}

        try:
            # Валидация
            validated_file = await image_validator.validate(file)

            # Сохранение (на диск + в БД)
            image_data = await image_service.upload_image(validated_file, batch_id, user_id, session)

            file_result.update({
                "status": "success",
                "image_id": image_data.id,
                "image_url": image_data.url_path
            })

        except HTTPException as e:
            # Ошибки валидации (400, 413)
            file_result.update({
                "status": "failed",
                "error": e.detail
            })
        except Exception as e:
            # Непредвиденные ошибки
            file_result.update({
                "status": "error",
                "error": f"Internal processing error: {str(e)}"
            })

        results.append(file_result)

    return {"batch_id": batch_id, "files": results}