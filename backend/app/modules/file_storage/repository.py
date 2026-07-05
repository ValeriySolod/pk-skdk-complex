"""Repository skeleton for the file storage module."""

from __future__ import annotations

from sqlalchemy.orm import Session


class FileStorageRepository:
    """Persistence boundary for future file storage metadata operations."""

    def __init__(self, db: Session) -> None:
        self.db = db


__all__ = ["FileStorageRepository"]
