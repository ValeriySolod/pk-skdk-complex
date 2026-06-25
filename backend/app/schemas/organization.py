from pydantic import BaseModel

class OrganizationBase(BaseModel):
    name: str
    edrpou: str | None = None
    address: str
    responsible_person: str | None = None
    phone: str | None = None

class OrganizationCreate(OrganizationBase):
    pass

class OrganizationRead(OrganizationBase):
    id: int
    model_config = {'from_attributes': True}
