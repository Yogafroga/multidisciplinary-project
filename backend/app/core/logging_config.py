import logging
import sys
from pathlib import Path


def setup_logging(log_level: str = "INFO") -> None:
    """
    Настраивает базовое логирование для приложения.
    
    Args:
        log_level: Уровень логирования (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    # Преобразуем строковый уровень в константу
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Формат логов
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    
    # Настройка root logger
    logging.basicConfig(
        level=numeric_level,
        format=log_format,
        datefmt=date_format,
        handlers=[
            logging.StreamHandler(sys.stdout)
        ],
        force=True  # Перезаписываем существующую конфигурацию
    )
    
    # Настройка уровней для сторонних библиотек
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("fastapi").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("boto3").setLevel(logging.WARNING)
    logging.getLogger("botocore").setLevel(logging.WARNING)
    logging.getLogger("aioboto3").setLevel(logging.WARNING)
    logging.getLogger("aiobotocore").setLevel(logging.WARNING)
    
    logger = logging.getLogger(__name__)
    logger.info(f"Logging configured with level: {log_level}")


def get_logger(name: str) -> logging.Logger:
    """
    Получить logger для модуля.
    
    Args:
        name: Имя модуля (обычно __name__)
        
    Returns:
        Настроенный logger
    """
    return logging.getLogger(name)

