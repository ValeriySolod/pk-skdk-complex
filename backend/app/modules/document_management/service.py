"""Service layer for the document management module."""

from __future__ import annotations

from app.modules.document_management.models import Document, DocumentVersion
from app.modules.document_management.repository import (
    DocumentRepository,
    DocumentVersionRepository,
)
from app.modules.document_management.schemas import DocumentCreate, DocumentUpdate


class DocumentManagementService:
    """Business boundary for document management operations."""

    def __init__(
        self,
        documents: DocumentRepository,
        versions: DocumentVersionRepository,
    ) -> None:
        self.documents = documents
        self.versions = versions

    def list_documents(self) -> list[Document]:
        raise NotImplementedError

    def get_document(self, document_id: int) -> Document | None:
        raise NotImplementedError

    def create_document(self, payload: DocumentCreate) -> Document:
        raise NotImplementedError

    def update_document(
        self,
        document_id: int,
        payload: DocumentUpdate,
    ) -> Document | None:
        raise NotImplementedError

    def list_document_versions(self, document_id: int) -> list[DocumentVersion]:
        raise NotImplementedError
