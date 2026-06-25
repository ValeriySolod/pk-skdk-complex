from app.core.module_registry import ModuleManifest, registry
from .router import router

def get_router():
    return router

registry.register(ModuleManifest(code='workflow', title='Технологічний процес', description='Етапи приймання, транзиту, доставки, контролю та архівування.', router_factory=get_router, permissions=['workflow:read', 'workflow:write']))
