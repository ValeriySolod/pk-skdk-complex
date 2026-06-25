from app.core.module_registry import ModuleManifest, registry
from .router import router

def get_router():
    return router

registry.register(ModuleManifest(
    code='organizations',
    title='Організації',
    description='Договірна база відправників та юридичних осіб.',
    router_factory=get_router,
    permissions=['organizations:read', 'organizations:write'],
))
