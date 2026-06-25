from dataclasses import dataclass, field
from typing import Callable
from fastapi import APIRouter

@dataclass(frozen=True)
class ModuleManifest:
    code: str
    title: str
    description: str
    router_factory: Callable[[], APIRouter]
    permissions: list[str] = field(default_factory=list)

class ModuleRegistry:
    def __init__(self) -> None:
        self._modules: dict[str, ModuleManifest] = {}

    def register(self, manifest: ModuleManifest) -> None:
        if manifest.code in self._modules:
            raise ValueError(f'Module already registered: {manifest.code}')
        self._modules[manifest.code] = manifest

    def include_all(self, api_router: APIRouter, prefix: str = '') -> None:
        for manifest in self._modules.values():
            api_router.include_router(manifest.router_factory(), prefix=f'{prefix}/{manifest.code}', tags=[manifest.title])

    def list(self) -> list[dict]:
        return [
            {'code': m.code, 'title': m.title, 'description': m.description, 'permissions': m.permissions}
            for m in self._modules.values()
        ]

registry = ModuleRegistry()
