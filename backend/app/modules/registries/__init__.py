from app.core.module_registry import ModuleManifest, registry
from .router import router

def get_router():
    return router

registry.register(ModuleManifest(
    code='registries',
    title='Реєстри',
    description='Створення та приймання реєстрів відправлень із QR-кодами.',
    router_factory=get_router,
    permissions=['registries:read', 'registries:write'],
))
