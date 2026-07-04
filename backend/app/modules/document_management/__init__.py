from fastapi import APIRouter

from app.core.module_registry import ModuleManifest, registry
from app.modules.document_management.models import (
    Document,
    DocumentAuditEvent,
    DocumentCategory,
    DocumentPermission,
    DocumentTag,
    DocumentTagAssignment,
    DocumentVersion,
)

from .routes import router


def get_router() -> APIRouter:
    return router


registry.register(
    ModuleManifest(
        code="document-management",
        title="Document Management",
        description="Document storage, metadata, versioning, and attachments.",
        router_factory=get_router,
        permissions=["document_management:read"],
    )
)


__all__ = [
    "Document",
    "DocumentAuditEvent",
    "DocumentCategory",
    "DocumentPermission",
    "DocumentTag",
    "DocumentTagAssignment",
    "DocumentVersion",
]
