"""Repository skeletons for the document management module."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.modules.document_management.models import Document, DocumentVersion


class DocumentRepository:
    """Persistence operations for documents."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, document_id: int) -> Document | None:
        raise NotImplementedError

    def list(self) -> list[Document]:
        raise NotImplementedError

    def create(self, document: Document) -> Document:
        raise NotImplementedError


class DocumentVersionRepository:
    """Persistence operations for document versions."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, document_version_id: int) -> DocumentVersion | None:
        raise NotImplementedError

    def list_by_document_id(self, document_id: int) -> list[DocumentVersion]:
        raise NotImplementedError

    def create(self, document_version: DocumentVersion) -> DocumentVersion:
        raise NotImplementedError


__all__ = [
    "DocumentRepository",
    "DocumentVersionRepository",
]
