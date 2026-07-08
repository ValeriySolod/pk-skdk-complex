"""Integrations module registration."""

from app.core.module_registry import registry

from .manifest import get_router, manifest

registry.register(manifest)

__all__ = [
    "get_router",
    "manifest",
]
