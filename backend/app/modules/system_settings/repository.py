"""Repository boundary for the System Settings module."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session


class SystemSettingsRepository:
    """Persistence boundary for system settings."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def health(self) -> bool:
        return self.db.scalar(select(1)) == 1
