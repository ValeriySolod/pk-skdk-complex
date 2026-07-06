"""Service layer for the Administration module."""

from __future__ import annotations

from app.modules.administration.repository import AdministrationRepository


class AdministrationService:
    """Business boundary for administration workflows."""

    def __init__(self, repository: AdministrationRepository) -> None:
        self.repository = repository

    def health(self) -> dict[str, str]:
        """Return module health based on the repository boundary."""
        status = "ok" if self.repository.health() else "degraded"
        return {"status": status}
