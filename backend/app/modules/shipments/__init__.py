from app.core.module_registry import ModuleManifest, registry
from .router import router

def get_router():
    return router

registry.register(ModuleManifest(
    code='shipments',
    title='Відправлення',
    description='Картки опису відправлень, маршрутизація, статуси доставки.',
    router_factory=get_router,
    permissions=['shipments:read', 'shipments:write', 'shipments:control'],
))
