import uuid
from typing import List
from fastapi import APIRouter, UploadFile, File, status, HTTPException

from backend.app.services.image_service import image_service
from backend.app.utils.validators import image_validator

router = APIRouter(tags=['Upload'])

@router.post("/upload_image", status_code=status.HTTP_201_CREATED)
async def upload_single_image(file: UploadFile = File(...)):
    """
    Загрузка одного изображения с валидацией.
    """
    # 1. Валидация
    validated_file = await image_validator.validate(file)
    
    # 2. Генерация папки
    subfolder = str(uuid.uuid4())
    
    # 3. Сохранение
    try:
        saved_path = await image_service.save_file(validated_file, subfolder)
        return {
            "message": "File uploaded successfully", 
            "filename": saved_path
        }
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Не удалось сохранить файл на сервере"
        )


@router.post("/upload_images", status_code=status.HTTP_200_OK)
async def upload_multiple_images(files: List[UploadFile] = File(...)):
    """
    Массовая загрузка изображений.
    Возвращает статус по каждому файлу отдельно.
    """
    results = []
    batch_id = str(uuid.uuid4()) # Все файлы из одного запроса кладем в одну папку

    for file in files:
        file_result = {"filename": file.filename, "status": "pending"}
        
        try:
            # Валидация
            validated_file = await image_validator.validate(file)
            
            # Сохранение
            saved_path = await image_service.save_file(validated_file, batch_id)
            
            file_result.update({
                "status": "success",
                "path": saved_path
            })
            
        except HTTPException as e:
            # Ошибки валидации (400, 413)
            file_result.update({
                "status": "failed",
                "error": e.detail
            })
        except Exception:
            # Непредвиденные ошибки
            file_result.update({
                "status": "error",
                "error": "Internal processing error"
            })
            
        results.append(file_result)

    return {"batch_id": batch_id, "files": results}