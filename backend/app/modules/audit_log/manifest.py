"""Audit Log module manifest."""

from fastapi import APIRouter

from app.core.module_registry import ModuleManifest

from .routes import router


def get_router() -> APIRouter:
    return router


manifest = ModuleManifest(
    code="audit-log",
    title="Audit Log",
    description="User activity log, change history, and security audit.",
    router_factory=get_router,
    permissions=["audit_log:read"],
)
