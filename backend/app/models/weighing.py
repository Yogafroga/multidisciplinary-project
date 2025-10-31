from sqlalchemy import ForeignKey, Float, String
from sqlalchemy.orm import Mapped, mapped_column
from backend.app.database import Base, int_pk


class Weighing(Base):
    id: Mapped[int_pk]
    animal_id: Mapped[int] = mapped_column(ForeignKey('animals.id'), nullable=False)
    predicted_weight: Mapped[float] = mapped_column(Float(precision=53), nullable=False)
    image_url: Mapped[str] = mapped_column(String(300), nullable=False)
