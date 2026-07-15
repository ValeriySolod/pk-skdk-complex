from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column
from app.db import Base

class Registry(Base):
    __tablename__ = 'registries'
    id: Mapped[int] = mapped_column(primary_key=True)
    number: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    sender_org_id: Mapped[int] = mapped_column(ForeignKey('organizations.id'), index=True)
    received_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    qr_payload: Mapped[str | None] = mapped_column(String(500), nullable=True)
    status: Mapped[str] = mapped_column(String(40), default='created')
