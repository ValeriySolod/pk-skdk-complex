from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class DocumentCreate(BaseModel):
    pass


class DocumentUpdate(BaseModel):
    pass


class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int


class DocumentVersionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
