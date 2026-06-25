from app.core.module_registry import ModuleManifest, registry
from .router import router

def get_router():
    return router

registry.register(ModuleManifest(
    code='scanner',
    title='Сканування',
    description='Пошук і автоматична зміна стану доставки при скануванні штрих/QR-коду.',
    router_factory=get_router,
    permissions=['scanner:scan'],
))
