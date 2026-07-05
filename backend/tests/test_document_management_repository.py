from __future__ import annotations

from uuid import uuid4

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


def create_document(
    repository: DocumentRepository,
    title: str = "Repository Procedure",
    document_number: str = "DOC-006-8",
    status: str = "draft",
) -> Document:
    return repository.create(
        Document(
            title=title,
            document_number=document_number,
            description="Repository integration test document",
            document_type="procedure",
            status=status,
        ),
    )


def test_document_create_list_lookup_update_delete_and_missing_results(
    db_session: Session,
) -> None:
    repository = DocumentRepository(db_session)

    document = create_document(repository)
    second_document = create_document(
        repository,
        title="Archive Register",
        document_number="DOC-ARCH-001",
        status="active",
    )

    assert document.id is not None
    assert repository.list() == [document, second_document]
    assert repository.get_by_id(document.id) == document
    assert repository.get_by_id(999) is None
    assert repository.get_by_uuid(uuid4()) is None
    assert repository.exists(document.id) is True
    assert repository.exists(999) is False
    assert repository.search("Procedure") == [document]
    assert repository.search("ARCH") == [second_document]
    assert repository.search("missing") == []

    updated_document = repository.update(
        document.id,
        {"title": "Updated Procedure", "status": "active"},
    )

    assert updated_document is document
    assert document.title == "Updated Procedure"
    assert document.document_number == "DOC-006-8"
    assert document.status == "active"
    assert repository.update(999, {"status": "archived"}) is None

    assert repository.delete(document.id) is True
    assert repository.get_by_id(document.id) is None
    assert repository.delete(document.id) is False
    assert repository.list() == [second_document]


def test_document_version_create_list_latest_and_missing_results(
    db_session: Session,
) -> None:
    document_repository = DocumentRepository(db_session)
    version_repository = DocumentVersionRepository(db_session)
    document = create_document(document_repository)

    first_version = version_repository.create(
        DocumentVersion(
            document_id=document.id,
            version="1.0",
            file_name="procedure-v1.pdf",
            storage_path="/documents/procedure-v1.pdf",
            checksum="checksum-v1",
        ),
    )
    second_version = version_repository.create_version(
        DocumentVersion(
            document_id=document.id,
            version="2.0",
            file_name="procedure-v2.pdf",
            storage_path="/documents/procedure-v2.pdf",
            checksum="checksum-v2",
        ),
    )

    assert first_version.id is not None
    assert second_version.id is not None
    assert version_repository.get_by_id(first_version.id) == first_version
    assert version_repository.get_by_id(999) is None
    assert version_repository.list_by_document_id(document.id) == [
        first_version,
        second_version,
    ]
    assert version_repository.list_versions(document.id) == [
        first_version,
        second_version,
    ]
    assert version_repository.get_latest(document.id) == second_version
    assert version_repository.list_by_document_id(999) == []
    assert version_repository.get_latest(999) is None


def test_document_category_create_tree_update_delete_and_missing_results(
    db_session: Session,
) -> None:
    repository = DocumentCategoryRepository(db_session)

    policy_category = repository.create(
        DocumentCategory(
            name="Policies",
            code="POLICY",
            description="Policy documents",
        ),
    )
    procedure_category = repository.create(
        DocumentCategory(
            name="Procedures",
            code="PROCEDURE",
            description="Procedure documents",
        ),
    )

    assert policy_category.id is not None
    assert repository.get_tree() == [policy_category, procedure_category]
    assert repository.get_by_id(policy_category.id) == policy_category
    assert repository.get_by_id(999) is None

    updated_category = repository.update(
        policy_category.id,
        {"name": "Active Policies", "is_active": False},
    )

    assert updated_category is policy_category
    assert policy_category.name == "Active Policies"
    assert policy_category.code == "POLICY"
    assert policy_category.is_active is False
    assert repository.update(999, {"name": "Missing"}) is None

    assert repository.delete(policy_category.id) is True
    assert repository.get_by_id(policy_category.id) is None
    assert repository.delete(policy_category.id) is False
    assert repository.get_tree() == [procedure_category]


def test_document_attachment_create_list_remove_and_missing_results(
    db_session: Session,
) -> None:
    document_repository = DocumentRepository(db_session)
    attachment_repository = DocumentAttachmentRepository(db_session)
    version_repository = DocumentVersionRepository(db_session)
    document = create_document(document_repository)

    attachment = attachment_repository.add_attachment(
        DocumentVersion(
            document_id=document.id,
            version="attachment-1",
            file_name="evidence.pdf",
            storage_path="/documents/evidence.pdf",
            checksum="attachment-checksum",
        ),
    )

    assert attachment.id is not None
    assert attachment_repository.list_for_document(document.id) == [attachment]
    assert version_repository.get_by_id(attachment.id) == attachment
    assert attachment_repository.list_for_document(999) == []

    assert attachment_repository.remove_attachment(attachment.id) is True
    assert version_repository.get_by_id(attachment.id) is None
    assert attachment_repository.remove_attachment(attachment.id) is False
