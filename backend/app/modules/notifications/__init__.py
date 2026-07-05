from fastapi import APIRouter

from app.core.module_registry import ModuleManifest, registry

from .routes import router


def get_router() -> APIRouter:
    return router


registry.register(
    ModuleManifest(
        code="notifications",
        title="Notifications",
        description="In-app notifications, email notifications, and system alerts.",
        router_factory=get_router,
        permissions=["notifications:read"],
    )
)


__all__ = ["get_router"]
