import aiofiles
import uuid
from pathlib import Path
from fastapi import UploadFile
from backend.app.core.config import settings


def generate_filename(original_filename: str) -> str:
    """
    Генерирует уникальное имя файла на основе UUID.
    Сохраняет расширение из оригинального имени.
    """
    ext = original_filename.split(".")[-1].lower() if "." in original_filename else "bin"
    return f"{uuid.uuid4()}.{ext}"


async def save_file(file: UploadFile, subfolder_name: str) -> dict:
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
    try:
        # Гарантируем, что базовая папка существует
        settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

        # Создаем подпапку (например, UUID батча)
        subfolder_path = settings.UPLOAD_DIR / subfolder_name
        subfolder_path.mkdir(exist_ok=True)

        # Генерируем безопасное имя файла
        filename = generate_filename(file.filename)
        file_path = subfolder_path / filename

        # Потоковая запись (chunked writing)
        # Это экономит память, если файлов много
        file_size = 0
        async with aiofiles.open(file_path, 'wb') as out_file:
            while content := await file.read(1024 * 1024):  # Читаем по 1 МБ
                await out_file.write(content)
                file_size += len(content)

        # Возвращаем информацию о сохраненном файле
        return {
            "file_path": str(file_path),
            "filename": filename,
            "original_filename": file.filename,
            "subfolder": subfolder_name,
            "file_size": file_size,
            "mime_type": file.content_type
        }

    except OSError as e:
        # Логируем ошибку ввода-вывода
        print(f"Disk I/O error: {e}")
        raise e
