from app.core.module_registry import ModuleManifest, registry
from .router import router

def get_router():
    return router

registry.register(ModuleManifest(
    code='search',
    title='Пошук',
    description='Пошук карток за реквізитами, контекстом, штрих-кодом та фільтрами.',
    router_factory=get_router,
    permissions=['search:read'],
))
