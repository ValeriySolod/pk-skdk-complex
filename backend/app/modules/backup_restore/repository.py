"""Repository operations for the Backup & Restore module."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session


class BackupRestoreRepository:
    """Persistence boundary for backup and restore readiness checks."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def health(self) -> bool:
        """Return whether the persistence boundary is available."""

        return self.db.scalar(select(1)) == 1

    def health_check(self) -> bool:
        return self.health()


__all__ = ["BackupRestoreRepository"]
