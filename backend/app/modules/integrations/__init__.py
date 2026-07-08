"""Integrations module registration."""

from app.core.module_registry import registry

from .manifest import get_router, manifest
from .models import (
    IntegrationConnection,
    IntegrationConnectionStatus,
    IntegrationEvent,
    IntegrationEventStatus,
    IntegrationProvider,
    IntegrationProviderStatus,
    IntegrationSyncJob,
    IntegrationSyncJobStatus,
)

registry.register(manifest)

__all__ = [
    "IntegrationConnection",
    "IntegrationConnectionStatus",
    "IntegrationEvent",
    "IntegrationEventStatus",
    "IntegrationProvider",
    "IntegrationProviderStatus",
    "IntegrationSyncJob",
    "IntegrationSyncJobStatus",
    "get_router",
    "manifest",
]
