import aiofiles
import uuid
from pathlib import Path
from fastapi import UploadFile
from backend.app.core.config import settings

class ImageService:
    def __init__(self):
        # Гарантируем, что базовая папка существует
        settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    async def save_file(self, file: UploadFile, subfolder_name: str) -> str:
        """
        Асинхронно сохраняет файл на диск.
        Возвращает относительный путь к файлу.
        """
        try:
            # Создаем подпапку (например, UUID батча)
            subfolder_path = settings.UPLOAD_DIR / subfolder_name
            subfolder_path.mkdir(exist_ok=True)

            # Генерируем безопасное имя файла
            # Берем расширение из MIME типа или из имени, если уверены (после валидации можно брать из имени)
            ext = file.filename.split(".")[-1].lower() if "." in file.filename else "bin"
            filename = f"{uuid.uuid4()}.{ext}"
            file_path = subfolder_path / filename

            # Потоковая запись (chunked writing)
            # Это экономит память, если файлов много
            async with aiofiles.open(file_path, 'wb') as out_file:
                while content := await file.read(1024 * 1024):  # Читаем по 1 МБ
                    await out_file.write(content)

            # Возвращаем путь строкой (можно вернуть относительный путь для URL)
            # Например: backend/data/<uuid>/<uuid>.jpg
            return str(file_path)
            
        except OSError as e:
            # Логируем ошибку ввода-вывода
            print(f"Disk I/O error: {e}")
            raise e

image_service = ImageService()