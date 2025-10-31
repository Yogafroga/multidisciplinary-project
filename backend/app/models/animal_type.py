from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from backend.app.database import Base, str_uniq, int_pk


class Animal_type(Base):
    id: Mapped[int_pk]
    type: Mapped[str_uniq] = mapped_column(String(50), nullable=False)
