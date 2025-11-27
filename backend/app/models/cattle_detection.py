import uuid
import sqlalchemy as sa
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID  # Импортируем нативный UUID Postgres

# Импорт твоего Base
from backend.app.database import Base 


class CattleDetection(Base):
    __tablename__ = 'cattle_detections'

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    
    # ID объекта от нейронки (0, 1, 2...)
    nn_object_id = sa.Column(sa.Integer, nullable=True) 
    
    weight = sa.Column(sa.Float, nullable=True) 
    
    create_datetime = sa.Column(sa.DateTime(timezone=True), server_default=func.now())
    
    image_id = sa.Column(sa.Integer, sa.ForeignKey("images.id"), nullable=False)
    
    image = relationship("Image", back_populates="detections")