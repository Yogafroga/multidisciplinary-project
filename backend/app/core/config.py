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