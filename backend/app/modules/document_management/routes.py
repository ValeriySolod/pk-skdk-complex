from typing import NoReturn
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.dependencies import get_db
from app.models import User
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
from app.modules.document_management.schemas import (
    DocumentAttachmentCreate,
    DocumentAttachmentRead,
    DocumentCategoryCreate,
    DocumentCategoryRead,
    DocumentCategoryUpdate,
    DocumentCreate,
    DocumentManagementHealthRead,
    DocumentResponse,
    DocumentUpdate,
    DocumentVersionCreate,
    DocumentVersionResponse,
)
from app.modules.document_management.service import DocumentManagementService


router = APIRouter()


def get_document_management_service(
    db: Session = Depends(get_db),
) -> DocumentManagementService:
    return DocumentManagementService(
        documents=DocumentRepository(db),
        versions=DocumentVersionRepository(db),
        categories=DocumentCategoryRepository(db),
        attachments=DocumentAttachmentRepository(db),
    )


def raise_bad_request(exc: ValueError) -> NoReturn:
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=str(exc),
    ) from exc


def raise_not_found(detail: str) -> NoReturn:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=detail,
    )


@router.get("/health", response_model=DocumentManagementHealthRead)
def module_health(_: User = Depends(get_current_user)) -> dict[str, str]:
    return {"status": "ok"}


@router.get("/documents", response_model=list[DocumentResponse])
def list_documents(
    service: DocumentManagementService = Depends(get_document_management_service),
    _: User = Depends(get_current_user),
) -> list[Document]:
    return service.list_documents()


@router.post(
    "/documents",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_document(
    payload: DocumentCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> Document:
    service = get_document_management_service(db)
    try:
        document = service.create_document(payload)
    except ValueError as exc:
        raise_bad_request(exc)
    db.commit()
    db.refresh(document)
    return document


@router.get("/documents/uuid/{document_uuid}", response_model=DocumentResponse)
def get_document_by_uuid(
    document_uuid: UUID,
    service: DocumentManagementService = Depends(get_document_management_service),
    _: User = Depends(get_current_user),
) -> Document:
    document = service.get_document_by_uuid(document_uuid)
    if document is None:
        raise_not_found("Document not found")
    return document


@router.get("/documents/{document_id}", response_model=DocumentResponse)
def get_document(
    document_id: int,
    service: DocumentManagementService = Depends(get_document_management_service),
    _: User = Depends(get_current_user),
) -> Document:
    document = service.get_document(document_id)
    if document is None:
        raise_not_found("Document not found")
    return document


@router.patch("/documents/{document_id}", response_model=DocumentResponse)
def update_document(
    document_id: int,
    payload: DocumentUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> Document:
    service = get_document_management_service(db)
    try:
        document = service.update_document(document_id, payload)
    except ValueError as exc:
        raise_bad_request(exc)
    if document is None:
        raise_not_found("Document not found")
    db.commit()
    db.refresh(document)
    return document


@router.delete("/documents/{document_id}")
def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> dict[str, bool]:
    service = get_document_management_service(db)
    deleted = service.delete_document(document_id)
    if not deleted:
        raise_not_found("Document not found")
    db.commit()
    return {"deleted": True}


@router.patch(
    "/documents/{document_id}/status/{document_status}",
    response_model=DocumentResponse,
)
def set_document_status(
    document_id: int,
    document_status: str,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> Document:
    service = get_document_management_service(db)
    try:
        document = service.set_document_status(document_id, document_status)
    except ValueError as exc:
        raise_bad_request(exc)
    if document is None:
        raise_not_found("Document not found")
    db.commit()
    db.refresh(document)
    return document


@router.post("/documents/{document_id}/archive", response_model=DocumentResponse)
def archive_document(
    document_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> Document:
    service = get_document_management_service(db)
    document = service.archive_document(document_id)
    if document is None:
        raise_not_found("Document not found")
    db.commit()
    db.refresh(document)
    return document


@router.post("/documents/{document_id}/activate", response_model=DocumentResponse)
def activate_document(
    document_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> Document:
    service = get_document_management_service(db)
    document = service.activate_document(document_id)
    if document is None:
        raise_not_found("Document not found")
    db.commit()
    db.refresh(document)
    return document


@router.get(
    "/documents/{document_id}/versions",
    response_model=list[DocumentVersionResponse],
)
def list_document_versions(
    document_id: int,
    service: DocumentManagementService = Depends(get_document_management_service),
    _: User = Depends(get_current_user),
) -> list[DocumentVersion]:
    try:
        return service.list_document_versions(document_id)
    except ValueError:
        raise_not_found("Document not found")


@router.post(
    "/documents/{document_id}/versions",
    response_model=DocumentVersionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_document_version(
    document_id: int,
    payload: DocumentVersionCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> DocumentVersion:
    service = get_document_management_service(db)
    if payload.document_id != document_id:
        raise_bad_request(ValueError("Document id mismatch"))
    try:
        document_version = service.create_version(
            DocumentVersion(**payload.model_dump()),
        )
    except ValueError as exc:
        raise_bad_request(exc)
    db.commit()
    db.refresh(document_version)
    return document_version


@router.get(
    "/documents/{document_id}/versions/latest",
    response_model=DocumentVersionResponse,
)
def get_latest_document_version(
    document_id: int,
    service: DocumentManagementService = Depends(get_document_management_service),
    _: User = Depends(get_current_user),
) -> DocumentVersion:
    try:
        document_version = service.get_latest_document_version(document_id)
    except ValueError:
        raise_not_found("Document not found")
    if document_version is None:
        raise_not_found("Document version not found")
    return document_version


@router.get("/versions/{document_version_id}", response_model=DocumentVersionResponse)
def get_document_version(
    document_version_id: int,
    service: DocumentManagementService = Depends(get_document_management_service),
    _: User = Depends(get_current_user),
) -> DocumentVersion:
    document_version = service.get_document_version(document_version_id)
    if document_version is None:
        raise_not_found("Document version not found")
    return document_version


@router.get("/categories", response_model=list[DocumentCategoryRead])
def list_document_categories(
    service: DocumentManagementService = Depends(get_document_management_service),
    _: User = Depends(get_current_user),
) -> list[DocumentCategory]:
    return service.list_document_categories()


@router.post(
    "/categories",
    response_model=DocumentCategoryRead,
    status_code=status.HTTP_201_CREATED,
)
def create_document_category(
    payload: DocumentCategoryCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> DocumentCategory:
    service = get_document_management_service(db)
    try:
        category = service.create_document_category(
            DocumentCategory(**payload.model_dump()),
        )
    except ValueError as exc:
        raise_bad_request(exc)
    db.commit()
    db.refresh(category)
    return category


@router.get("/categories/{category_id}", response_model=DocumentCategoryRead)
def get_document_category(
    category_id: int,
    service: DocumentManagementService = Depends(get_document_management_service),
    _: User = Depends(get_current_user),
) -> DocumentCategory:
    category = service.get_document_category(category_id)
    if category is None:
        raise_not_found("Document category not found")
    return category


@router.patch("/categories/{category_id}", response_model=DocumentCategoryRead)
def update_document_category(
    category_id: int,
    payload: DocumentCategoryUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> DocumentCategory:
    service = get_document_management_service(db)
    try:
        category = service.update_document_category(
            category_id,
            payload.model_dump(exclude_unset=True),
        )
    except ValueError as exc:
        raise_bad_request(exc)
    if category is None:
        raise_not_found("Document category not found")
    db.commit()
    db.refresh(category)
    return category


@router.delete("/categories/{category_id}")
def delete_document_category(
    category_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> dict[str, bool]:
    service = get_document_management_service(db)
    deleted = service.delete_document_category(category_id)
    if not deleted:
        raise_not_found("Document category not found")
    db.commit()
    return {"deleted": True}


@router.get(
    "/documents/{document_id}/attachments",
    response_model=list[DocumentAttachmentRead],
)
def list_document_attachments(
    document_id: int,
    service: DocumentManagementService = Depends(get_document_management_service),
    _: User = Depends(get_current_user),
) -> list[DocumentVersion]:
    try:
        return service.list_document_attachments(document_id)
    except ValueError:
        raise_not_found("Document not found")


@router.post(
    "/documents/{document_id}/attachments",
    response_model=DocumentAttachmentRead,
    status_code=status.HTTP_201_CREATED,
)
def add_document_attachment(
    document_id: int,
    payload: DocumentAttachmentCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> DocumentVersion:
    service = get_document_management_service(db)
    if payload.document_id != document_id:
        raise_bad_request(ValueError("Document id mismatch"))
    try:
        document_version = service.add_document_attachment(
            DocumentVersion(**payload.model_dump()),
        )
    except ValueError as exc:
        raise_bad_request(exc)
    db.commit()
    db.refresh(document_version)
    return document_version


@router.get(
    "/attachments/{document_version_id}",
    response_model=DocumentAttachmentRead,
)
def get_document_attachment(
    document_version_id: int,
    service: DocumentManagementService = Depends(get_document_management_service),
    _: User = Depends(get_current_user),
) -> DocumentVersion:
    document_version = service.get_document_attachment(document_version_id)
    if document_version is None:
        raise_not_found("Document attachment not found")
    return document_version


@router.delete("/attachments/{document_version_id}")
def remove_document_attachment(
    document_version_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> dict[str, bool]:
    service = get_document_management_service(db)
    deleted = service.remove_document_attachment(document_version_id)
    if not deleted:
        raise_not_found("Document attachment not found")
    db.commit()
    return {"deleted": True}
