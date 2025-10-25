from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from backend.app.database import Base, str_uniq, int_pk


class User(Base):
    id: Mapped[int_pk]
    login: Mapped[str_uniq] = mapped_column(String(50))
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
