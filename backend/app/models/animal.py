from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from backend.app.database import Base, int_pk


class Animal(Base):
    id: Mapped[int_pk]
    type_id: Mapped[int] = mapped_column(ForeignKey('animal_types.id'), nullable=False)
