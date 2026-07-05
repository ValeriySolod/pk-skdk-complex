"""Repository skeletons for the document management module."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from uuid import UUID

from sqlalchemy import select
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
        self.db.add(document)
        self.db.flush()
        return document

    def update(
        self,
        document_id: int,
        values: Mapping[str, object],
    ) -> Document | None:
        document = self.get_by_id(document_id)
        if document is None:
            return None

        for field, value in values.items():
            setattr(document, field, value)

        self.db.flush()
        return document

    def delete(self, document_id: int) -> bool:
        document = self.get_by_id(document_id)
        if document is None:
            return False

        self.db.delete(document)
        self.db.flush()
        return True

    def get_by_id(self, document_id: int) -> Document | None:
        return self.db.get(Document, document_id)

    def get_by_uuid(self, document_uuid: UUID) -> Document | None:
        uuid_column = getattr(Document, "document_uuid", None)
        if uuid_column is None:
            uuid_column = getattr(Document, "uuid", None)
        if uuid_column is None:
            return None

        return self.db.scalar(select(Document).where(uuid_column == document_uuid))

    def list(self) -> Sequence[Document]:
        return list(self.db.scalars(select(Document).order_by(Document.id)).all())

    def search(self, query: str) -> Sequence[Document]:
        pattern = f"%{query}%"
        return list(
            self.db.scalars(
                select(Document)
                .where(
                    Document.title.ilike(pattern)
                    | Document.document_number.ilike(pattern)
                    | Document.description.ilike(pattern),
                )
                .order_by(Document.id),
            ).all(),
        )

    def exists(self, document_id: int) -> bool:
        return self.get_by_id(document_id) is not None


class DocumentVersionRepository:
    """Persistence operations for document versions."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, document_version_id: int) -> DocumentVersion | None:
        return self.db.get(DocumentVersion, document_version_id)

    def list_by_document_id(self, document_id: int) -> Sequence[DocumentVersion]:
        return list(
            self.db.scalars(
                select(DocumentVersion)
                .where(DocumentVersion.document_id == document_id)
                .order_by(DocumentVersion.id),
            ).all(),
        )

    def create(self, document_version: DocumentVersion) -> DocumentVersion:
        self.db.add(document_version)
        self.db.flush()
        return document_version

    def create_version(self, document_version: DocumentVersion) -> DocumentVersion:
        return self.create(document_version)

    def get_latest(self, document_id: int) -> DocumentVersion | None:
        return self.db.scalar(
            select(DocumentVersion)
            .where(DocumentVersion.document_id == document_id)
            .order_by(DocumentVersion.id.desc()),
        )

    def list_versions(self, document_id: int) -> Sequence[DocumentVersion]:
        return self.list_by_document_id(document_id)


class DocumentCategoryRepository:
    """Persistence operations for document categories."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, category: DocumentCategory) -> DocumentCategory:
        self.db.add(category)
        self.db.flush()
        return category

    def update(
        self,
        category_id: int,
        values: Mapping[str, object],
    ) -> DocumentCategory | None:
        category = self.get_by_id(category_id)
        if category is None:
            return None

        for field, value in values.items():
            setattr(category, field, value)

        self.db.flush()
        return category

    def delete(self, category_id: int) -> bool:
        category = self.get_by_id(category_id)
        if category is None:
            return False

        self.db.delete(category)
        self.db.flush()
        return True

    def get_tree(self) -> Sequence[DocumentCategory]:
        return list(
            self.db.scalars(select(DocumentCategory).order_by(DocumentCategory.id)).all(),
        )

    def get_by_id(self, category_id: int) -> DocumentCategory | None:
        return self.db.get(DocumentCategory, category_id)


class DocumentAttachmentRepository:
    """Persistence operations for document file attachments."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def add_attachment(self, document_version: DocumentVersion) -> DocumentVersion:
        self.db.add(document_version)
        self.db.flush()
        return document_version

    def remove_attachment(self, document_version_id: int) -> bool:
        document_version = self.db.get(DocumentVersion, document_version_id)
        if document_version is None:
            return False

        self.db.delete(document_version)
        self.db.flush()
        return True

    def list_for_document(self, document_id: int) -> Sequence[DocumentVersion]:
        return list(
            self.db.scalars(
                select(DocumentVersion)
                .where(DocumentVersion.document_id == document_id)
                .order_by(DocumentVersion.id),
            ).all(),
        )


__all__ = [
    "DocumentAttachmentRepository",
    "DocumentCategoryRepository",
    "DocumentRepository",
    "DocumentVersionRepository",
]
