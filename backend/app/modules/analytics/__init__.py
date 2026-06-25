from app.core.module_registry import ModuleManifest, registry
from .router import router

def get_router():
    return router

registry.register(ModuleManifest(code='analytics', title='Аналітика', description='Аналітика навантаження, прогнозування та контроль процесів.', router_factory=get_router, permissions=['analytics:read']))
