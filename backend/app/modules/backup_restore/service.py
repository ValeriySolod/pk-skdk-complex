"""Service layer for the Backup & Restore module."""

from __future__ import annotations

from app.modules.backup_restore.repository import BackupRestoreRepository
from app.modules.backup_restore.schemas import BackupRestoreHealthRead


class BackupRestoreService:
    """Business boundary for backup and restore workflows."""

    def __init__(self, repository: BackupRestoreRepository) -> None:
        self.repository = repository

    def health(self) -> BackupRestoreHealthRead:
        """Return aggregate Backup & Restore module health."""

        return BackupRestoreHealthRead(
            module="backup_restore",
            status="ok" if self.repository.health() else "error",
        )


__all__ = ["BackupRestoreService"]
