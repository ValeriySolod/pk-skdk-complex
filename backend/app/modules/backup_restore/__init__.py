"""Backup & Restore module registration."""

from app.core.module_registry import registry

from .manifest import get_router, manifest
from .models import (
    BackupJob,
    BackupJobStatus,
    BackupJobType,
    RestoreJob,
    RestoreJobStatus,
)

registry.register(manifest)

__all__ = [
    "BackupJob",
    "BackupJobStatus",
    "BackupJobType",
    "RestoreJob",
    "RestoreJobStatus",
    "get_router",
    "manifest",
]
