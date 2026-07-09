"""Monitoring & Health module manifest."""

from fastapi import APIRouter

from app.core.module_registry import ModuleManifest

from .routes import router


def get_router() -> APIRouter:
    return router


manifest = ModuleManifest(
    code="monitoring_health",
    title="Monitoring & Health",
    description="Health checks, diagnostics, and operational monitoring.",
    router_factory=get_router,
    permissions=["monitoring_health:read", "monitoring_health:write"],
)
