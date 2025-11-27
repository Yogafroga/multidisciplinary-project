import uuid
import sqlalchemy as sa
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID  # Импортируем нативный UUID Postgres

# Импорт твоего Base
from backend.app.database import Base 

class ImageBatch(Base):
    __tablename__ = 'image_batches'

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    
    # Уникальный идентификатор пакета (он же имя папки)
    # default=uuid.uuid4 позволяет генерировать его автоматически при создании записи
    uid = sa.Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False, index=True)
    
    # Путь к папке (например: /media/uploads/e4d2.../)
    url_path = sa.Column(sa.String, nullable=True) 
    
    create_datetime = sa.Column(sa.DateTime(timezone=True), server_default=func.now())
    
    # Связь с пользователем
    user_id = sa.Column(sa.Integer, sa.ForeignKey("users.id"), nullable=False)

    user = relationship("User", back_populates="image_batches")
    images = relationship("Image", back_populates="batch", cascade="all, delete-orphan")

