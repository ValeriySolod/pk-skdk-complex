"""Backup & Restore module manifest."""

from fastapi import APIRouter

from app.core.module_registry import ModuleManifest

from .routes import router


def get_router() -> APIRouter:
    return router


manifest = ModuleManifest(
    code="backup-restore",
    title="Backup & Restore",
    description="Backup creation, restore workflow, and data recovery procedures.",
    router_factory=get_router,
    permissions=["backup_restore:read"],
)
