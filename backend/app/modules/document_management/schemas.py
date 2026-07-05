from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DocumentManagementHealthRead(BaseModel):
    status: str


class DocumentBase(BaseModel):
    title: str
    document_number: str | None = None
    description: str | None = None
    document_type: str
    status: str
    organization_id: int | None = None
    owner_user_id: int | None = None


class DocumentCreate(DocumentBase):
    pass


class DocumentUpdate(BaseModel):
    title: str | None = None
    document_number: str | None = None
    description: str | None = None
    document_type: str | None = None
    status: str | None = None
    organization_id: int | None = None
    owner_user_id: int | None = None


class DocumentRead(DocumentBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class DocumentVersionBase(BaseModel):
    document_id: int
    version: str
    file_name: str
    storage_path: str
    checksum: str | None = None
    uploaded_by: int | None = None


class DocumentVersionCreate(DocumentVersionBase):
    pass


class DocumentVersionRead(DocumentVersionBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    uploaded_at: datetime


class DocumentCategoryBase(BaseModel):
    name: str
    code: str
    description: str | None = None
    is_active: bool = True


class DocumentCategoryCreate(DocumentCategoryBase):
    pass


class DocumentCategoryUpdate(BaseModel):
    name: str | None = None
    code: str | None = None
    description: str | None = None
    is_active: bool | None = None


class DocumentCategoryRead(DocumentCategoryBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class DocumentAttachmentCreate(DocumentVersionBase):
    pass


class DocumentAttachmentRead(DocumentVersionBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    uploaded_at: datetime


DocumentResponse = DocumentRead
DocumentVersionResponse = DocumentVersionRead
