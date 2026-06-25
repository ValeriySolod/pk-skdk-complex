from app.core.module_registry import ModuleManifest, registry
from .router import router

def get_router():
    return router

registry.register(ModuleManifest(code='admin', title='Адміністрування', description='Ролі, права доступу, календар змін, системні налаштування.', router_factory=get_router, permissions=['admin:write']))
