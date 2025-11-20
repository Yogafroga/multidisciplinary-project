from fastapi import UploadFile, HTTPException, status
from typing import Dict
from PIL import Image, UnidentifiedImageError
from io import BytesIO
from backend.app.core.config import settings
import logging

# Настраиваем логгер (в реальном проекте он настроен глобально)
logger = logging.getLogger(__name__)

class ImageValidator:
    """
    Класс для валидации изображений.
    Сопоставляет настройки проекта с базой известных сигнатур.
    """

    # БАЗА ЗНАНИЙ: Сигнатуры, которые наш код "знает" в принципе.
    # Если в конфиге появится тип, которого нет здесь - мы должны узнать об этом сразу.
    KNOWN_SIGNATURES: Dict[str, bytes] = {
        "image/jpeg": b"\xFF\xD8\xFF",
        "image/png":  b"\x89\x50\x4E\x47\x0D\x0A\x1A\x0A",
        "image/gif":  b"\x47\x49\x46\x38",
        "image/webp": b"\x52\x49\x46\x46",
        # Можно добавить bmp, tiff и т.д.
        "image/bmp":  b"\x42\x4D",
    }

    def __init__(self):
        self.max_size = settings.max_bytes
        # Берем разрешенные типы ИМЕННО из конфига
        self.allowed_mimes = settings.ALLOWED_MIME_TYPES
        
        # === FAIL FAST CHECK ===
        # Проверяем при старте: есть ли у нас сигнатуры для всех разрешенных типов?
        self._validate_config_integrity()

    def _validate_config_integrity(self):
        """Гарантирует, что для каждого разрешенного в конфиге типа есть сигнатура."""
        for mime in self.allowed_mimes:
            if mime not in self.KNOWN_SIGNATURES:
                error_msg = (
                    f"CRITICAL CONFIG ERROR: Тип '{mime}' разрешен в settings.py, "
                    f"но для него нет HEX-сигнатуры в ImageValidator.KNOWN_SIGNATURES."
                )
                logger.critical(error_msg)
                # В продакшене тут лучше рейзить ошибку, чтобы не запустить сломанное приложение
                raise RuntimeError(error_msg)

    async def validate(self, file: UploadFile) -> UploadFile:
        """Основной метод валидации."""
        
        # 1. Проверка MIME-типа (декларируемого клиентом) по списку из КОНФИГА
        if file.content_type not in self.allowed_mimes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Тип файла '{file.content_type}' не поддерживается. Разрешены: {', '.join(self.allowed_mimes)}"
            )

        # 2. Проверка размера (по content-length заголовка, если есть, для скорости)
        # Но основная проверка будет ниже после чтения
        
        # 3. Проверка Сигнатуры (Magic Numbers)
        # Читаем столько байт, сколько в самой длинной сигнатуре (PNG = 8, но берем с запасом 16)
        header = await file.read(16)
        await file.seek(0)  # Возвращаем курсор!

        expected_signature = self.KNOWN_SIGNATURES.get(file.content_type)
        
        # Если signature нет, значит _validate_config_integrity пропустил ошибку (чего быть не должно)
        # Но на всякий случай:
        if not expected_signature:
             raise HTTPException(status_code=500, detail="Server misconfiguration for this file type")

        if not header.startswith(expected_signature):
             raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Файл поддельный! Содержимое не соответствует расширению."
            )

        # 4. Проверка полного содержимого (Размер + PIL)
        content = await file.read()
        
        if len(content) > self.max_size:
             raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"Файл слишком большой. Лимит: {settings.MAX_FILE_SIZE_MB} МБ"
            )

        try:
            img = Image.open(BytesIO(content))
            img.verify()
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Файл поврежден."
            )

        await file.seek(0)
        return file

# Создаем экземпляр
image_validator = ImageValidator()