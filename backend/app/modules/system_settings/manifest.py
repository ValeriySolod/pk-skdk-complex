"""System Settings module manifest."""

from fastapi import APIRouter

from app.core.module_registry import ModuleManifest

from .routes import router


def get_router() -> APIRouter:
    return router


manifest = ModuleManifest(
    code="system-settings",
    title="System Settings",
    description="Configurable application settings and defaults.",
    router_factory=get_router,
    permissions=["system_settings:read"],
)
