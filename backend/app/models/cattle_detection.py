# backend/app/models/cattle_detection.py
import sqlalchemy as sa
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from backend.app.database import Base 


class CattleDetection(Base):
    __tablename__ = 'cattle_detections'

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    
    # ID объекта от нейронки (0, 1, 2...)
    nn_object_id = sa.Column(sa.Integer, nullable=True) 
    
    # Идентификатор животного (номер бирки) — обязательное
    animal_id = sa.Column(sa.String(50), nullable=False, index=True)
    
    # Предсказанный вес — может не прийти от ML
    weight = sa.Column(sa.Float, nullable=True) 
    
    # Уверенность модели (0.0 - 1.0) — может не прийти от ML
    confidence = sa.Column(sa.Float, nullable=True)
    
    create_datetime = sa.Column(sa.DateTime(timezone=True), server_default=func.now())
    
    # FK к изображению — обязательное
    image_id = sa.Column(sa.Integer, sa.ForeignKey("images.id"), nullable=False)
    
    image = relationship("Image", back_populates="detections")