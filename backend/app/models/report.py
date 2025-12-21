from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from backend.app.database import Base, int_pk


class Report(Base):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    name: Mapped[str] = mapped_column(String(25), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
