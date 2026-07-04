from app.core.module_registry import ModuleManifest, registry

from .routes import router


def get_router():
    return router


registry.register(
    ModuleManifest(
        code="user-management",
        title="User Management",
        description="User CRUD, role assignment, and permissions management.",
        router_factory=get_router,
        permissions=["user_management:read"],
    )
)
