from datetime import date
from sqlalchemy import Date, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.db import Base

class Contract(Base):
    __tablename__ = 'contracts'
    id: Mapped[int] = mapped_column(primary_key=True)
    organization_id: Mapped[int] = mapped_column(ForeignKey('organizations.id'), index=True)
    number: Mapped[str] = mapped_column(String(100), index=True)
    signed_at: Mapped[date] = mapped_column(Date)
    valid_until: Mapped[date | None] = mapped_column(Date, nullable=True)
    confidentiality_clause: Mapped[bool] = mapped_column(default=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
