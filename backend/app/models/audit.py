from sqlalchemy import Column, Integer, String, ARRAY, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.database import Base


class Audit(Base):
    __tablename__ = "audit"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'),
                                         nullable=True)
    url: Mapped[str] = mapped_column(String)
    headers = Column("headers", ARRAY(String))
    method: Mapped[str] = mapped_column(String)
    response: Mapped[str] = mapped_column(String)

    user = relationship("User", back_populates="audits")