# backend/app/core/config.py
import os
from pathlib import Path
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Базовые настройки приложения
    PROJECT_NAME: str = "CattleWeighAI"
    
    # Настройки загрузки файлов
    UPLOAD_DIR: Path = Path("backend/data")
    MAX_FILE_SIZE_MB: int = 5

    # Настройки VK Cloud S3
    VK_S3_ENDPOINT_URL: str = "https://hb.ru-msk.vkcloud-storage.ru"
    VK_S3_REGION: str = "ru-msk"
    VK_S3_BUCKET_NAME: str
    VK_S3_ACCESS_KEY_ID: str
    VK_S3_SECRET_KEY: str
    
    # Разрешенные типы (MIME)
    ALLOWED_MIME_TYPES: set[str] = {
        "image/jpeg", 
        "image/png", 
        "image/gif", 
        "image/webp"
    }

    @property
    def max_bytes(self) -> int:
        return self.MAX_FILE_SIZE_MB * 1024 * 1024

    class Config:
        env_file = ".env"

settings = Settings()
