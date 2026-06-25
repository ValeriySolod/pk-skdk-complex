from datetime import datetime
from enum import Enum
from sqlalchemy import DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

class AccessMark(str, Enum):
    NOT_SECRET = 'НЕ СЕКРЕТНО'
    SECRET = 'СЕКРЕТНО'

class ShipmentStatus(str, Enum):
    DRAFT = 'draft'
    REGISTERED = 'registered'
    ACCEPTED = 'accepted'
    TRANSIT = 'transit'
    IN_DELIVERY = 'in_delivery'
    DELIVERED = 'delivered'
    ARCHIVED = 'archived'

class Shipment(Base):
    __tablename__ = 'shipments'
    id: Mapped[int] = mapped_column(primary_key=True)
    barcode: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    registry_id: Mapped[int | None] = mapped_column(ForeignKey('registries.id'), nullable=True, index=True)
    sender_org_id: Mapped[int | None] = mapped_column(ForeignKey('organizations.id'), nullable=True)
    recipient_name: Mapped[str] = mapped_column(String(255), index=True)
    recipient_address: Mapped[str] = mapped_column(Text)
    document_number: Mapped[str | None] = mapped_column(String(120), index=True, nullable=True)
    document_date: Mapped[str | None] = mapped_column(String(40), nullable=True)
    weight_kg: Mapped[float | None] = mapped_column(Float, nullable=True)
    access_mark: Mapped[str] = mapped_column(String(40), default=AccessMark.NOT_SECRET.value)
    region: Mapped[str | None] = mapped_column(String(120), index=True, nullable=True)
    district: Mapped[str | None] = mapped_column(String(120), index=True, nullable=True)
    status: Mapped[str] = mapped_column(String(40), default=ShipmentStatus.REGISTERED.value, index=True)
    accepted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    delivered_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    current_assignee_id: Mapped[int | None] = mapped_column(ForeignKey('users.id'), nullable=True)
