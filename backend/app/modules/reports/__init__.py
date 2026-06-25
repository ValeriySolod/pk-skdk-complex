from app.core.module_registry import ModuleManifest, registry
from .router import router

def get_router():
    return router

registry.register(ModuleManifest(
    code='reports',
    title='Звіти',
    description='Статистичні та карткові звіти для друку й експорту.',
    router_factory=get_router,
    permissions=['reports:read', 'reports:export'],
))
