from app.core.module_registry import ModuleManifest, registry

from .router import router


def get_router():
    return router


registry.register(
    ModuleManifest(
        code="organization-structure",
        title="Organization Structure",
        description="Organizational hierarchy, departments, positions, and employees.",
        router_factory=get_router,
        permissions=["organization_structure:read"],
    )
)
