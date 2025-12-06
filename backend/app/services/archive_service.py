# backend/app/services/archive_service.py
import zipfile
import asyncio
import aioboto3
from pathlib import Path
from typing import List, Tuple
from io import BytesIO
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from backend.app.services.image_service import image_service
from backend.app.repositories.batch_image_repository import batch_image_repository
from backend.app.core.config import settings

ALLOWED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}

class ArchiveService:
    
    async def process_archive(
        self,
        file: UploadFile,
        batch_id: str,
        user_id: int,
        session: AsyncSession
    ) -> Tuple[List[dict], List[dict]]:
        
        successful = []
        failed = []

        # 1. Сначала создаем батч в БД (один раз)
        batch_uuid = uuid.UUID(batch_id)
        batch = await batch_image_repository.get_or_create(session, user_id, batch_uuid)

        # Читаем архив в память
        content = await file.read()
        
        try:
            with zipfile.ZipFile(BytesIO(content), 'r') as zip_ref:
                file_list = zip_ref.namelist()
                
                # Подготовка задач
                tasks = []
                # Семафор ограничивает кол-во одновременных загрузок (чтобы не убить память/сеть)
                semaphore = asyncio.Semaphore(10) 

                # Функция-воркер для одного файла
                async def process_single_file(file_name, s3_client_instance):
                    async with semaphore:
                        # Проверки имени
                        if file_name.endswith('/') or file_name.startswith('__MACOSX') or file_name.startswith('.'):
                            return None
                        
                        ext = Path(file_name).suffix.lower()
                        if ext not in ALLOWED_IMAGE_EXTENSIONS:
                            return None

                        try:
                            # Читаем байты из zip (это синхронная операция, но быстрая в памяти)
                            image_data = zip_ref.read(file_name)
                            
                            # Создаем UploadFile
                            upload_file = self._create_upload_file(file_name, image_data, ext)
                            animal_id = self._extract_animal_id(file_name)

                            # ЗАГРУЗКА (Параллельная часть, IO Bound)
                            file_data = await image_service.process_file_upload(
                                upload_file, 
                                batch_id, 
                                s3_client=s3_client_instance
                            )
                            
                            return {
                                "status": "success",
                                "file_data": file_data,
                                "animal_id": animal_id,
                                "original_name": Path(file_name).name
                            }

                        except Exception as e:
                            return {
                                "status": "error",
                                "filename": Path(file_name).name,
                                "error": str(e)
                            }

                # 2. Запускаем параллельную загрузку
                # Создаем сессию S3 один раз на весь архив
                aioboto3_session = aioboto3.Session()
                
                # Используем контекстный менеджер для клиента S3
                if all([settings.VK_S3_ENDPOINT_URL, settings.VK_S3_ACCESS_KEY_ID]):
                     async with aioboto3_session.client(
                        service_name='s3',
                        endpoint_url=settings.VK_S3_ENDPOINT_URL,
                        aws_access_key_id=settings.VK_S3_ACCESS_KEY_ID,
                        aws_secret_access_key=settings.VK_S3_SECRET_KEY,
                        region_name=settings.VK_S3_REGION
                    ) as s3_client:
                        
                        for name in file_list:
                            tasks.append(process_single_file(name, s3_client))
                        
                        results = await asyncio.gather(*tasks)
                else:
                    # Если локальное сохранение, клиент не нужен
                    for name in file_list:
                        tasks.append(process_single_file(name, None))
                    results = await asyncio.gather(*tasks)

            # 3. Обработка результатов и запись в БД (Последовательная часть)
            # Мы делаем это здесь, так как AsyncSession нельзя использовать конкурентно
            for res in results:
                if res is None:
                    continue
                
                if res["status"] == "error":
                    failed.append(res)
                    continue
                
                # Запись в БД
                try:
                    image, detection = await image_service.create_db_entries(
                        session=session,
                        file_data=res["file_data"],
                        batch_id=batch.id,
                        animal_id=res["animal_id"]
                    )
                    
                    successful.append({
                        "filename": res["original_name"],
                        "status": "success",
                        "image_id": image.id,
                        "image_url": image.url_path,
                        "weight": detection.weight,
                        "confidence": detection.confidence
                    })
                except Exception as e:
                    failed.append({
                        "filename": res["original_name"],
                        "status": "error",
                        "error": f"DB Error: {str(e)}"
                    })

        except zipfile.BadZipFile:
            failed.append({
                "filename": file.filename,
                "status": "error",
                "error": "Некорректный ZIP-архив"
            })
        
        return successful, failed

    def _create_upload_file(self, filename: str, content: bytes, ext: str) -> UploadFile:
        mime_types = {
            '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg',
            '.png': 'image/png', '.gif': 'image/gif', '.webp': 'image/webp'
        }
        content_type = mime_types.get(ext, 'application/octet-stream')
        return UploadFile(file=BytesIO(content), filename=Path(filename).name, size=len(content), headers={"content-type": content_type})

    def _extract_animal_id(self, filename: str) -> str:
        name = Path(filename).stem
        if '_' in name:
            parts = name.split('_')
            last_part = parts[-1]
            if last_part.isalnum():
                return last_part
        return name

    def calculate_summary(self, successful: List[dict]) -> dict:
        weights = [item["weight"] for item in successful if item.get("weight") is not None]
        if not weights:
            return {"total_weight": 0.0, "average_weight": 0.0, "animal_count": 0, "min_weight": None, "max_weight": None}
        return {
            "total_weight": round(sum(weights), 2),
            "average_weight": round(sum(weights) / len(weights), 2),
            "animal_count": len(weights),
            "min_weight": round(min(weights), 2),
            "max_weight": round(max(weights), 2)
        }

archive_service = ArchiveService()