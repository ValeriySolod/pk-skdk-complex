"""Repository skeletons for the document management module."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from uuid import UUID

from sqlalchemy.orm import Session

from app.modules.document_management.models import (
    Document,
    DocumentCategory,
    DocumentVersion,
)


class DocumentRepository:
    """Persistence operations for documents."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, document: Document) -> Document:
        raise NotImplementedError

    def update(
        self,
        document_id: int,
        values: Mapping[str, object],
    ) -> Document | None:
        raise NotImplementedError

    def delete(self, document_id: int) -> bool:
        raise NotImplementedError

    def get_by_id(self, document_id: int) -> Document | None:
        raise NotImplementedError

    def get_by_uuid(self, document_uuid: UUID) -> Document | None:
        raise NotImplementedError

    def list(self) -> Sequence[Document]:
        raise NotImplementedError

    def search(self, query: str) -> Sequence[Document]:
        raise NotImplementedError

    def exists(self, document_id: int) -> bool:
        raise NotImplementedError


class DocumentVersionRepository:
    """Persistence operations for document versions."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, document_version_id: int) -> DocumentVersion | None:
        raise NotImplementedError

    def list_by_document_id(self, document_id: int) -> Sequence[DocumentVersion]:
        raise NotImplementedError

    def create(self, document_version: DocumentVersion) -> DocumentVersion:
        raise NotImplementedError

    def create_version(self, document_version: DocumentVersion) -> DocumentVersion:
        raise NotImplementedError

    def get_latest(self, document_id: int) -> DocumentVersion | None:
        raise NotImplementedError

    def list_versions(self, document_id: int) -> Sequence[DocumentVersion]:
        raise NotImplementedError


class DocumentCategoryRepository:
    """Persistence operations for document categories."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, category: DocumentCategory) -> DocumentCategory:
        raise NotImplementedError

    def update(
        self,
        category_id: int,
        values: Mapping[str, object],
    ) -> DocumentCategory | None:
        raise NotImplementedError

    def delete(self, category_id: int) -> bool:
        raise NotImplementedError

    def get_tree(self) -> Sequence[DocumentCategory]:
        raise NotImplementedError

    def get_by_id(self, category_id: int) -> DocumentCategory | None:
        raise NotImplementedError


class DocumentAttachmentRepository:
    """Persistence operations for document file attachments."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def add_attachment(self, document_version: DocumentVersion) -> DocumentVersion:
        raise NotImplementedError

    def remove_attachment(self, document_version_id: int) -> bool:
        raise NotImplementedError

    def list_for_document(self, document_id: int) -> Sequence[DocumentVersion]:
        raise NotImplementedError


__all__ = [
    "DocumentAttachmentRepository",
    "DocumentCategoryRepository",
    "DocumentRepository",
    "DocumentVersionRepository",
]
