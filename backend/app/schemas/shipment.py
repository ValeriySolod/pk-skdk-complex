from datetime import datetime
from pydantic import BaseModel

class ShipmentBase(BaseModel):
    barcode: str
    registry_id: int | None = None
    sender_org_id: int | None = None
    recipient_name: str
    recipient_address: str
    document_number: str | None = None
    document_date: str | None = None
    weight_kg: float | None = None
    access_mark: str = 'НЕ СЕКРЕТНО'
    region: str | None = None
    district: str | None = None

class ShipmentCreate(ShipmentBase):
    pass

class ShipmentUpdate(BaseModel):
    status: str | None = None
    current_assignee_id: int | None = None
    delivered_at: datetime | None = None

class ShipmentRead(ShipmentBase):
    id: int
    status: str
    accepted_at: datetime | None = None
    delivered_at: datetime | None = None
    current_assignee_id: int | None = None
    model_config = {'from_attributes': True}

class ScanRequest(BaseModel):
    barcode: str
    event: str = 'scan'
    next_status: str | None = None
