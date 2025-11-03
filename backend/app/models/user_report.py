from sqlalchemy import ForeignKey, Table, Column, Integer
from sqlalchemy.orm import Mapped, mapped_column
from backend.app.database import Base

class User_report(Base):
  
    __tablename__ = 'user_reports'

    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), primary_key=True, nullable=False)
    report_id: Mapped[int] = mapped_column(ForeignKey('reports.id'), primary_key=True, nullable=False)

    created_at = None
    updated_at = None