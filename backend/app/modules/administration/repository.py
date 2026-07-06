"""Repository boundary for the Administration module."""

from __future__ import annotations

from sqlalchemy.orm import Session


class AdministrationRepository:
    """Persistence boundary for administration data and maintenance operations."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def health(self) -> bool:
        """Return whether the administration persistence boundary is available."""
        return self.db is not None
