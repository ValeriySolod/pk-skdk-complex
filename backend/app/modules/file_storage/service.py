"""Service layer skeleton for the file storage module."""

from __future__ import annotations

from app.modules.file_storage.repository import FileStorageRepository


class FileStorageService:
    """Business boundary for future file storage operations."""

    def __init__(self, repository: FileStorageRepository) -> None:
        self.repository = repository

    def health(self) -> dict[str, str]:
        return {"status": "ok"}
