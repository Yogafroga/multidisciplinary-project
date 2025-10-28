from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from backend.app.database import Base, str_uniq, int_pk


class User_role(Base):
    id: Mapped[int_pk]
    role: Mapped[str_uniq] = mapped_column(String(10))
