"""Administration module registration."""

from fastapi import APIRouter

from app.core.module_registry import ModuleManifest, registry

from .routes import router


def get_router() -> APIRouter:
    return router


registry.register(
    ModuleManifest(
        code="administration",
        title="Адміністрування",
        description="Application administration, reference data, maintenance tools.",
        router_factory=get_router,
        permissions=["administration:read", "administration:write"],
    )
)


__all__ = ["get_router"]
