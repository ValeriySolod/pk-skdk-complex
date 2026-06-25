from datetime import datetime
from pydantic import BaseModel

class RegistryCreate(BaseModel):
    number: str
    sender_org_id: int
    qr_payload: str | None = None

class RegistryRead(RegistryCreate):
    id: int
    received_at: datetime
    status: str
    model_config = {'from_attributes': True}
