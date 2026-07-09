"""Monitoring & Health module registration."""

from app.core.module_registry import registry

from .manifest import get_router, manifest
from .repository import MonitoringHealthRepository
from .schemas import MonitoringHealthHealthRead
from .service import MonitoringHealthService

registry.register(manifest)

__all__ = [
    "MonitoringHealthHealthRead",
    "MonitoringHealthRepository",
    "MonitoringHealthService",
    "get_router",
    "manifest",
]
