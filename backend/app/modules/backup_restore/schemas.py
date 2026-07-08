"""Pydantic schemas for the Backup & Restore module API contract."""

from __future__ import annotations

from pydantic import BaseModel


class BackupRestoreHealthRead(BaseModel):
    """Backup & Restore module health response."""

    status: str
    module: str


__all__ = ["BackupRestoreHealthRead"]
