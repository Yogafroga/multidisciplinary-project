from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from backend.app.database import Base, int_pk

class Report(Base):
  id: Mapped[int_pk]
  url: Mapped[str] = mapped_column(String(500), nullable=False)