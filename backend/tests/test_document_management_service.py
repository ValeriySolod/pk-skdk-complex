from __future__ import annotations

from uuid import uuid4

import pytest
from sqlalchemy.orm import Session

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
from app.modules.document_management.service import DocumentManagementService


@pytest.fixture()
def service(db_session: Session) -> DocumentManagementService:
    return DocumentManagementService(
        documents=DocumentRepository(db_session),
        versions=DocumentVersionRepository(db_session),
        categories=DocumentCategoryRepository(db_session),
        attachments=DocumentAttachmentRepository(db_session),
    )


def create_test_document(
    service: DocumentManagementService,
    title: str = "Service Procedure",
    document_number: str = "DOC-006-9",
    status: str = "draft",
) -> Document:
    return service.create_document(
        DocumentCreate(
            title=title,
            document_number=document_number,
            description="Created through the service layer",
            document_type="procedure",
            status=status,
        ),
    )


def create_test_version(
    service: DocumentManagementService,
    document_id: int,
    version: str = "1.0",
) -> DocumentVersion:
    return service.create_document_version(
        DocumentVersion(
            document_id=document_id,
            version=version,
            file_name=f"procedure-{version}.pdf",
            storage_path=f"/documents/procedure-{version}.pdf",
            checksum=f"checksum-{version}",
        ),
    )


def test_document_create_lookup_search_update_status_and_delete(
    service: DocumentManagementService,
) -> None:
    document = create_test_document(service)
    second_document = create_test_document(
        service,
        title="Archive Register",
        document_number="DOC-ARCH-006-9",
        status="active",
    )

    assert document.id is not None
    assert service.list_documents() == [document, second_document]
    assert service.get_document(document.id) == document
    assert service.get_document(999) is None
    assert service.get_document_by_uuid(uuid4()) is None
    assert service.document_exists(document.id) is True
    assert service.document_exists(999) is False
    assert service.require_document(document.id) == document
    assert service.search_documents("Procedure") == [document]
    assert service.search_documents("ARCH") == [second_document]
    assert service.search_documents("missing") == []

    updated_document = service.update_document(
        document.id,
        DocumentUpdate(title="Updated Procedure", status="active"),
    )

    assert updated_document is document
    assert document.title == "Updated Procedure"
    assert document.document_number == "DOC-006-9"
    assert document.status == "active"
    assert service.update_document(999, DocumentUpdate(status="archived")) is None

    archived_document = service.archive_document(document.id)
    assert archived_document is document
    assert document.status == "archived"

    activated_document = service.activate_document(document.id)
    assert activated_document is document
    assert document.status == "active"

    custom_status_document = service.set_document_status(document.id, "review")
    assert custom_status_document is document
    assert document.status == "review"
    assert service.set_document_status(999, "active") is None

    with pytest.raises(ValueError, match="Document status is required"):
        service.set_document_status(document.id, "")

    assert service.delete_document(document.id) is True
    assert service.get_document(document.id) is None
    assert service.delete_document(document.id) is False
    assert service.list_documents() == [second_document]


def test_require_document_raises_for_missing_document(
    service: DocumentManagementService,
) -> None:
    with pytest.raises(ValueError, match="Document not found"):
        service.require_document(999)


def test_version_create_lookup_latest_and_missing_document_guards(
    service: DocumentManagementService,
) -> None:
    document = create_test_document(service)
    first_version = create_test_version(service, document.id, "1.0")
    second_version = service.create_version(
        DocumentVersion(
            document_id=document.id,
            version="2.0",
            file_name="procedure-2.0.pdf",
            storage_path="/documents/procedure-2.0.pdf",
            checksum="checksum-2.0",
        ),
    )

    assert first_version.id is not None
    assert second_version.id is not None
    assert service.get_document_version(first_version.id) == first_version
    assert service.get_document_version(999) is None
    assert service.list_document_versions(document.id) == [
        first_version,
        second_version,
    ]
    assert service.list_versions(document.id) == [first_version, second_version]
    assert service.get_latest_document_version(document.id) == second_version

    with pytest.raises(ValueError, match="Document not found"):
        service.create_document_version(
            DocumentVersion(
                document_id=999,
                version="1.0",
                file_name="missing.pdf",
                storage_path="/documents/missing.pdf",
            ),
        )

    with pytest.raises(ValueError, match="Document not found"):
        service.create_version(
            DocumentVersion(
                document_id=999,
                version="1.0",
                file_name="missing-alias.pdf",
                storage_path="/documents/missing-alias.pdf",
            ),
        )

    with pytest.raises(ValueError, match="Document not found"):
        service.list_document_versions(999)

    with pytest.raises(ValueError, match="Document not found"):
        service.get_latest_document_version(999)


def test_category_create_list_lookup_update_delete_and_missing_results(
    service: DocumentManagementService,
) -> None:
    policy_category = service.create_document_category(
        DocumentCategory(
            name="Policies",
            code="POLICY",
            description="Policy documents",
        ),
    )
    procedure_category = service.create_document_category(
        DocumentCategory(
            name="Procedures",
            code="PROCEDURE",
            description="Procedure documents",
        ),
    )

    assert policy_category.id is not None
    assert service.list_document_categories() == [policy_category, procedure_category]
    assert service.get_document_category(policy_category.id) == policy_category
    assert service.get_document_category(999) is None

    updated_category = service.update_document_category(
        policy_category.id,
        {"name": "Active Policies", "is_active": False},
    )

    assert updated_category is policy_category
    assert policy_category.name == "Active Policies"
    assert policy_category.code == "POLICY"
    assert policy_category.is_active is False
    assert service.update_document_category(999, {"name": "Missing"}) is None

    assert service.delete_document_category(policy_category.id) is True
    assert service.get_document_category(policy_category.id) is None
    assert service.delete_document_category(policy_category.id) is False
    assert service.list_document_categories() == [procedure_category]


def test_attachment_create_list_lookup_remove_and_missing_document_guards(
    service: DocumentManagementService,
) -> None:
    document = create_test_document(service)

    attachment = service.add_document_attachment(
        DocumentVersion(
            document_id=document.id,
            version="attachment-1",
            file_name="evidence.pdf",
            storage_path="/documents/evidence.pdf",
            checksum="attachment-checksum",
        ),
    )

    assert attachment.id is not None
    assert service.list_document_attachments(document.id) == [attachment]
    assert service.get_document_attachment(attachment.id) == attachment
    assert service.get_document_attachment(999) is None

    with pytest.raises(ValueError, match="Document not found"):
        service.add_document_attachment(
            DocumentVersion(
                document_id=999,
                version="attachment-missing",
                file_name="missing.pdf",
                storage_path="/documents/missing.pdf",
            ),
        )

    with pytest.raises(ValueError, match="Document not found"):
        service.list_document_attachments(999)

    assert service.remove_document_attachment(attachment.id) is True
    assert service.get_document_attachment(attachment.id) is None
    assert service.remove_document_attachment(attachment.id) is False
