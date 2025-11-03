from sqlalchemy.orm import Mapped
from backend.app.database import Base, int_pk


class Animal(Base):
    id: Mapped[int_pk]
