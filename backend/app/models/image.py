import uuid
import sqlalchemy as sa
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID  # Импортируем нативный UUID Postgres

# Импорт твоего Base
from backend.app.database import Base

class Image(Base):
    __tablename__ = 'images'

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    
    # Уникальное имя файла (для файловой системы)
    uid = sa.Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False, index=True)
    
    # Оригинальное имя файла, которое загрузил юзер (например "IMG_2024.jpg")
    # Чтобы показывать его в интерфейсе
    original_name = sa.Column(sa.String, nullable=True) 
    
    # Полный путь (например: /media/uploads/batch_uuid/image_uuid.jpg)
    url_path = sa.Column(sa.String, nullable=False)
    
    status = sa.Column(sa.String, default="UPLOADED") 
    create_datetime = sa.Column(sa.DateTime(timezone=True), server_default=func.now())
    
    batch_id = sa.Column(sa.Integer, sa.ForeignKey("image_batches.id"), nullable=False)
    
    batch = relationship("ImageBatch", back_populates="images")
    detections = relationship("CattleDetection", back_populates="image", cascade="all, delete-orphan")