"""Service layer for the document management module."""

from __future__ import annotations

from uuid import UUID

from app.modules.document_management.models import (
    Document,
    DocumentCategory,
    DocumentVersion,
)
from app.modules.document_management.repository import (
    DocumentAttachmentRepository,
    DocumentCategoryRepository,
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
        categories: DocumentCategoryRepository,
        attachments: DocumentAttachmentRepository,
    ) -> None:
        self.documents = documents
        self.versions = versions
        self.categories = categories
        self.attachments = attachments

    def list_documents(self) -> list[Document]:
        return list(self.documents.list())

    def search_documents(self, query: str) -> list[Document]:
        return list(self.documents.search(query))

    def get_document(self, document_id: int) -> Document | None:
        return self.documents.get_by_id(document_id)

    def get_document_by_uuid(self, document_uuid: UUID) -> Document | None:
        return self.documents.get_by_uuid(document_uuid)

    def document_exists(self, document_id: int) -> bool:
        return self.documents.exists(document_id)

    def require_document(self, document_id: int) -> Document:
        return self._require_document(document_id)

    def create_document(self, payload: DocumentCreate) -> Document:
        document = Document(**payload.model_dump())
        return self.documents.create(document)

    def update_document(
        self,
        document_id: int,
        payload: DocumentUpdate,
    ) -> Document | None:
        values: dict[str, object] = payload.model_dump(exclude_unset=True)

        return self.documents.update(document_id, values)

    def set_document_status(
        self,
        document_id: int,
        status: str,
    ) -> Document | None:
        if not status:
            raise ValueError("Document status is required")

        return self.documents.update(document_id, {"status": status})

    def archive_document(self, document_id: int) -> Document | None:
        return self.set_document_status(document_id, "archived")

    def activate_document(self, document_id: int) -> Document | None:
        return self.set_document_status(document_id, "active")

    def delete_document(self, document_id: int) -> bool:
        return self.documents.delete(document_id)

    def list_document_versions(self, document_id: int) -> list[DocumentVersion]:
        self._require_document(document_id)
        return list(self.versions.list_by_document_id(document_id))

    def list_versions(self, document_id: int) -> list[DocumentVersion]:
        return list(self.versions.list_versions(document_id))

    def get_document_version(
        self,
        document_version_id: int,
    ) -> DocumentVersion | None:
        return self.versions.get_by_id(document_version_id)

    def get_latest_document_version(
        self,
        document_id: int,
    ) -> DocumentVersion | None:
        self._require_document(document_id)
        return self.versions.get_latest(document_id)

    def create_document_version(
        self,
        document_version: DocumentVersion,
    ) -> DocumentVersion:
        self._require_document(document_version.document_id)
        return self.versions.create(document_version)

    def create_version(
        self,
        document_version: DocumentVersion,
    ) -> DocumentVersion:
        self._require_document(document_version.document_id)
        return self.versions.create_version(document_version)

    def list_document_categories(self) -> list[DocumentCategory]:
        return list(self.categories.get_tree())

    def get_document_category(
        self,
        category_id: int,
    ) -> DocumentCategory | None:
        return self.categories.get_by_id(category_id)

    def create_document_category(
        self,
        category: DocumentCategory,
    ) -> DocumentCategory:
        return self.categories.create(category)

    def update_document_category(
        self,
        category_id: int,
        values: dict[str, object],
    ) -> DocumentCategory | None:
        return self.categories.update(category_id, values)

    def delete_document_category(self, category_id: int) -> bool:
        return self.categories.delete(category_id)

    def list_document_attachments(
        self,
        document_id: int,
    ) -> list[DocumentVersion]:
        self._require_document(document_id)
        return list(self.attachments.list_for_document(document_id))

    def get_document_attachment(
        self,
        document_version_id: int,
    ) -> DocumentVersion | None:
        return self.versions.get_by_id(document_version_id)

    def add_document_attachment(
        self,
        document_version: DocumentVersion,
    ) -> DocumentVersion:
        self._require_document(document_version.document_id)
        return self.attachments.add_attachment(document_version)

    def remove_document_attachment(self, document_version_id: int) -> bool:
        return self.attachments.remove_attachment(document_version_id)

    def _require_document(self, document_id: int) -> Document:
        document = self.documents.get_by_id(document_id)
        if document is None:
            raise ValueError("Document not found")
        return document
