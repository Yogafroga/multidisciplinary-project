import aiofiles
import uuid
import io
from pathlib import Path
from fastapi import UploadFile
import aioboto3
from backend.app.core.config import settings


def generate_filename(original_filename: str) -> str:
    """
    Генерирует уникальное имя файла на основе UUID.
    Сохраняет расширение из оригинального имени.
    """
    ext = original_filename.split(".")[-1].lower() if "." in original_filename else "bin"
    return f"{uuid.uuid4()}.{ext}"


async def save_file_to_folder(file: UploadFile, subfolder_name: str) -> dict:
    """
    Асинхронно сохраняет файл на диск.

    Args:
        file: Загруженный файл
        subfolder_name: Имя подпапки (например, UUID батча)

    Returns:
        dict: {
            "file_path": str,           # Полный путь к файлу
            "filename": str,            # Сгенерированное имя файла
            "original_filename": str,   # Оригинальное имя файла
            "subfolder": str,           # Имя подпапки
            "file_size": int,           # Размер файла в байтах
            "mime_type": str            # MIME тип файла
        }
    """
    await file.seek(0)
    try:
        settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        subfolder_path = settings.UPLOAD_DIR / subfolder_name
        subfolder_path.mkdir(exist_ok=True)

        filename = generate_filename(file.filename)
        file_path = subfolder_path / filename

        file_size = 0
        async with aiofiles.open(file_path, 'wb') as out_file:
            while content := await file.read(1024 * 1024):
                await out_file.write(content)
                file_size += len(content)

        relative_url = f"/media/{subfolder_name}/{filename}"

        return {
            "file_path": str(file_path),
            "filename": filename,
            "original_filename": file.filename,
            "subfolder": subfolder_name,
            "file_size": file_size,
            "mime_type": file.content_type,
            "url": relative_url
        }
    except OSError as e:
        print(f"Disk I/O error: {e}")
        raise e


async def save_file_to_s3(file: UploadFile, subfolder_name: str, s3_client=None) -> dict:
    """
    Теперь принимает опциональный s3_client для переиспользования соединения.
    """
    await file.seek(0)  # Важно: сбросить курсор в начало
    try:
        filename = generate_filename(file.filename)
        s3_key = f"{subfolder_name}/{filename}"
        
        # Читаем файл целиком (для S3 это ок, если файлы не гигабайтные)
        file_content = await file.read()
        file_size = len(file_content)

        # Логика: если клиент передан - используем его, иначе создаем одноразовый
        if s3_client:
            await s3_client.put_object(
                Bucket=settings.VK_S3_BUCKET_NAME,
                Key=s3_key,
                Body=file_content,
                ContentType=file.content_type
            )
        else:
            session = aioboto3.Session()
            async with session.client(
                service_name='s3',
                endpoint_url=settings.VK_S3_ENDPOINT_URL,
                aws_access_key_id=settings.VK_S3_ACCESS_KEY_ID,
                aws_secret_access_key=settings.VK_S3_SECRET_KEY,
                region_name=settings.VK_S3_REGION
            ) as client:
                await client.put_object(
                    Bucket=settings.VK_S3_BUCKET_NAME,
                    Key=s3_key,
                    Body=file_content,
                    ContentType=file.content_type
                )

        file_url = f"{settings.VK_S3_ENDPOINT_URL}/{settings.VK_S3_BUCKET_NAME}/{s3_key}"

        return {
            "file_path": s3_key,
            "filename": filename,
            "original_filename": file.filename,
            "subfolder": subfolder_name,
            "file_size": file_size,
            "mime_type": file.content_type,
            "url": file_url
        }

    except Exception as e:
        print(f"S3 upload error: {e}")
        raise e