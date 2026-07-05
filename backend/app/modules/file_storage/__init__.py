from fastapi import APIRouter

from app.core.module_registry import ModuleManifest, registry

from .models import (
    FileObject,
    FileObjectStatus,
    FileObjectVisibility,
    StorageProvider,
    StoredFile,
)
from .routes import router


def get_router() -> APIRouter:
    return router


registry.register(
    ModuleManifest(
        code="file-storage",
        title="File Storage",
        description="File upload, download, metadata, and access rules.",
        router_factory=get_router,
        permissions=["file_storage:read"],
    )
)


__all__ = [
    "FileObject",
    "FileObjectStatus",
    "FileObjectVisibility",
    "StorageProvider",
    "StoredFile",
    "get_router",
]
