import uuid
from typing import List
from fastapi import APIRouter, UploadFile, File, status, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.services.image_service import image_service
from backend.app.utils.validators import image_validator
from backend.app.database import get_db

router = APIRouter(tags=['Upload'])

@router.post("/upload_image", status_code=status.HTTP_201_CREATED)
async def upload_single_image(
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_db)
):
    """
    Загрузка одного изображения с валидацией.
    Сохраняет файл на диск и информацию о нём в БД.
    """
    # 1. Валидация
    validated_file = await image_validator.validate(file)

    # 2. Генерация папки
    subfolder = str(uuid.uuid4())

    # 3. Сохранение (на диск + в БД)
    try:
        image_data = await image_service.upload_image(validated_file, subfolder, session)
        return {
            "message": "File uploaded successfully",
            "weighing_id": image_data.id,
            "image_url": image_data.image_url
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Не удалось сохранить файл: {str(e)}"
        )


@router.post("/upload_images", status_code=status.HTTP_200_OK)
async def upload_multiple_images(
    files: List[UploadFile] = File(...),
    session: AsyncSession = Depends(get_db)
):
    """
    Массовая загрузка изображений.
    Сохраняет файлы на диск и информацию о них в БД.
    Возвращает статус по каждому файлу отдельно.
    """
    results = []
    batch_id = str(uuid.uuid4())  # Все файлы из одного запроса кладем в одну папку

    for file in files:
        file_result = {"filename": file.filename, "status": "pending"}

        try:
            # Валидация
            validated_file = await image_validator.validate(file)

            # Сохранение (на диск + в БД)
            image_data = await image_service.upload_image(validated_file, batch_id, session)

            file_result.update({
                "status": "success",
                "weighing_id": image_data.id,
                "image_url": image_data.image_url
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